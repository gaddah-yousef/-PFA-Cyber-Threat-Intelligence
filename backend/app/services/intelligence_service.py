"""Exports CTI, corrélation multi-sources et détection d'écarts explicable."""

from collections import defaultdict
from datetime import datetime, timezone
from statistics import median
from uuid import NAMESPACE_URL, uuid4, uuid5

from app.models.threat import Threat


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _stix_id(kind: str, stable_key: str) -> str:
    return f"{kind}--{uuid5(NAMESPACE_URL, f'sentinel-pme:{kind}:{stable_key}')}"


def _escape_stix(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def build_stix_bundle(threats: list[Threat]) -> dict:
    pattern_by_type = {
        "ip": "ipv4-addr:value",
        "domain": "domain-name:value",
        "url": "url:value",
        "hash": "file:hashes.'SHA-256'",
    }
    objects: list[dict] = []
    for threat in threats:
        created = _iso(threat.created_at)
        modified = _iso(threat.last_seen)
        if threat.indicator_type == "cve":
            objects.append(
                {
                    "type": "vulnerability",
                    "spec_version": "2.1",
                    "id": _stix_id("vulnerability", threat.indicator),
                    "created": created,
                    "modified": modified,
                    "name": threat.indicator,
                    "description": threat.description,
                    "external_references": [
                        {
                            "source_name": "cve",
                            "external_id": threat.indicator,
                            "url": f"https://nvd.nist.gov/vuln/detail/{threat.indicator}",
                        }
                    ],
                }
            )
            continue

        pattern_field = pattern_by_type.get(threat.indicator_type)
        if pattern_field is None:
            continue
        objects.append(
            {
                "type": "indicator",
                "spec_version": "2.1",
                "id": _stix_id("indicator", f"{threat.indicator_type}:{threat.indicator}"),
                "created": created,
                "modified": modified,
                "name": threat.indicator,
                "description": threat.description,
                "indicator_types": ["malicious-activity"],
                "pattern": f"[{pattern_field} = '{_escape_stix(threat.indicator)}']",
                "pattern_type": "stix",
                "pattern_version": "2.1",
                "valid_from": _iso(threat.first_seen),
                "confidence": min(100, max(0, threat.risk_score)),
                "labels": [threat.threat_type, threat.risk_level, f"source:{threat.source}"],
            }
        )
    return {"type": "bundle", "id": f"bundle--{uuid4()}", "objects": objects}


def build_misp_event(threats: list[Threat]) -> dict:
    attribute_type = {
        "ip": "ip-dst",
        "domain": "domain",
        "url": "url",
        "hash": "sha256",
        "cve": "vulnerability",
    }
    attributes = [
        {
            "uuid": str(uuid5(NAMESPACE_URL, f"sentinel-pme:misp:{item.id}")),
            "type": attribute_type[item.indicator_type],
            "category": "External analysis",
            "value": item.indicator,
            "comment": f"Source: {item.source}; score: {item.risk_score}/100. {item.description}",
            "to_ids": item.risk_score >= 70,
            "distribution": "0",
        }
        for item in threats
        if item.indicator_type in attribute_type
    ]
    highest = max((item.risk_score for item in threats), default=0)
    return {
        "Event": {
            "uuid": str(uuid4()),
            "info": "Sentinel PME — export de Threat Intelligence",
            "date": datetime.now(timezone.utc).date().isoformat(),
            "published": False,
            "analysis": "2",
            "threat_level_id": "1" if highest >= 90 else "2" if highest >= 70 else "3",
            "distribution": "0",
            "Attribute": attributes,
        }
    }


def correlate_threats(threats: list[Threat]) -> list[dict]:
    grouped: dict[str, list[Threat]] = defaultdict(list)
    for threat in threats:
        grouped[threat.indicator.strip().lower()].append(threat)

    results = []
    for items in grouped.values():
        sources = sorted({item.source for item in items})
        if len(sources) < 2:
            continue
        max_score = max(item.risk_score for item in items)
        results.append(
            {
                "indicator": items[0].indicator,
                "indicator_type": items[0].indicator_type,
                "sources": sources,
                "source_count": len(sources),
                "threat_ids": [item.id for item in items],
                "max_risk_score": max_score,
                "confidence": min(100, 55 + 15 * len(sources)),
                "reason": f"Indicateur confirmé par {len(sources)} sources indépendantes.",
            }
        )
    return sorted(results, key=lambda item: (-item["confidence"], -item["max_risk_score"]))


def detect_score_anomalies(threats: list[Threat]) -> list[dict]:
    """Détecte les scores atypiquement élevés avec médiane/MAD.

    Cette méthode robuste et déterministe est présentée comme analytique
    expérimentale, jamais comme une décision automatique opaque.
    """

    if len(threats) < 5:
        return []
    scores = [item.risk_score for item in threats]
    center = float(median(scores))
    mad = float(median(abs(score - center) for score in scores))
    scale = mad if mad > 0 else 1.0
    results = []
    for item in threats:
        robust_z = 0.6745 * (item.risk_score - center) / scale
        # Le seuil absolu évite de signaler un petit écart lorsque MAD vaut 0.
        if item.risk_score < center + 25 or robust_z < 3.5:
            continue
        results.append(
            {
                "threat_id": item.id,
                "indicator": item.indicator,
                "observed_score": item.risk_score,
                "median_score": center,
                "mad": mad,
                "robust_z_score": round(robust_z, 2),
                "method": "median_mad",
                "reason": (
                    f"Score {item.risk_score}, supérieur de "
                    f"{item.risk_score - center:.0f} points à la médiane {center:.0f}."
                ),
            }
        )
    return sorted(results, key=lambda item: item["robust_z_score"], reverse=True)
