import csv
import io
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from app.collectors.base import BaseCollector, parse_source_datetime
from app.core.config import settings
from app.schemas.threat import ThreatInput


class URLhausCollector(BaseCollector):
    """Collecteur des URL récentes via l'export CSV communautaire URLhaus v2."""

    name = "urlhaus"
    endpoint_template = "https://urlhaus-api.abuse.ch/v2/files/exports/{auth_key}/recent.csv"

    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        if not settings.urlhaus_auth_key:
            raise ValueError("URLHAUS_AUTH_KEY n'est pas configurée")

        endpoint = self.endpoint_template.format(
            auth_key=quote(settings.urlhaus_auth_key, safe="")
        )
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(endpoint)
            response.raise_for_status()

        def csv_lines():
            for line in io.StringIO(response.text.lstrip("\ufeff")):
                stripped = line.strip()
                if stripped.lower().startswith("# id,"):
                    yield stripped[2:] + "\n"
                elif stripped and not stripped.startswith("#"):
                    yield line

        rows = csv.DictReader(csv_lines())

        now = datetime.now(timezone.utc)
        threats: list[ThreatInput] = []
        for item in rows:
            indicator = (item.get("url") or "").strip()
            if not indicator:
                continue
            threats.append(
                ThreatInput(
                    indicator=indicator,
                    indicator_type="url",
                    threat_type="malware",
                    source="urlhaus",
                    severity="high" if item.get("url_status") == "online" else "medium",
                    description=f"URLhaus — menace: {item.get('threat', 'malware')}",
                    first_seen=parse_source_datetime(
                        item.get("dateadded") or item.get("date_added"), now
                    ),
                    last_seen=now,
                )
            )
            if len(threats) >= limit:
                break
        return threats
