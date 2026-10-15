import logging
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.collectors.abuseipdb_collector import AbuseIPDBCollector
from app.collectors.base import BaseCollector
from app.collectors.nvd_collector import NVDCollector
from app.collectors.otx_collector import OTXCollector
from app.collectors.sample_collector import SampleCollector
from app.collectors.urlhaus_collector import URLhausCollector
from app.services.threat_service import analyze_and_save_threat
from app.services.vulnerability_enrichment import enrich_threat_inputs
from app.services.vulnerability_matching import refresh_all_asset_matches

logger = logging.getLogger(__name__)

COLLECTORS: dict[str, BaseCollector] = {
    collector.name: collector
    for collector in (
        SampleCollector(),
        URLhausCollector(),
        NVDCollector(),
        AbuseIPDBCollector(),
        OTXCollector(),
    )
}


async def run_collector(db: Session, name: str, limit: int = 20) -> int:
    """Exécute un collecteur et enregistre les menaces normalisées. Renvoie le
    nombre de menaces traitées (créées ou mises à jour)."""

    collector = COLLECTORS.get(name)
    if collector is None:
        raise KeyError(f"Collecteur inconnu: {name}")

    payloads = await collector.collect(limit=limit)
    if name == "nvd":
        payloads = await enrich_threat_inputs(payloads)
    for payload in payloads:
        analyze_and_save_threat(db, payload)
    if name == "nvd" and payloads:
        refresh_all_asset_matches(db)
    return len(payloads)


async def run_all_collectors(
    db: Session, limit: int = 20, names: Iterable[str] | None = None
) -> dict[str, int]:
    results: dict[str, int] = {}
    collector_names = COLLECTORS if names is None else names
    for name in collector_names:
        try:
            results[name] = await run_collector(db, name, limit=limit)
        except Exception:  # noqa: BLE001 - une source en panne ne doit pas bloquer les autres
            logger.exception("Échec de la collecte pour la source %s", name)
            results[name] = 0
    return results
