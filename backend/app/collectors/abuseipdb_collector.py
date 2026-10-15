from datetime import datetime, timezone

import httpx

from app.collectors.base import BaseCollector
from app.core.config import settings
from app.schemas.threat import ThreatInput


class AbuseIPDBCollector(BaseCollector):
    """Collecteur des adresses IP les plus signalées sur AbuseIPDB.

    Nécessite ABUSEIPDB_API_KEY (offre gratuite disponible sur abuseipdb.com).
    """

    name = "abuseipdb"
    endpoint = "https://api.abuseipdb.com/api/v2/blacklist"

    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        if not settings.abuseipdb_api_key:
            raise ValueError("ABUSEIPDB_API_KEY n'est pas configurée")

        headers = {"Key": settings.abuseipdb_api_key, "Accept": "application/json"}
        params = {"confidenceMinimum": 90, "limit": limit}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(self.endpoint, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        now = datetime.now(timezone.utc)
        threats: list[ThreatInput] = []
        for item in payload.get("data", [])[:limit]:
            score = item.get("abuseConfidenceScore", 90)
            threats.append(
                ThreatInput(
                    indicator=item["ipAddress"],
                    indicator_type="ip",
                    threat_type="suspicious_ip",
                    source="abuseipdb",
                    severity="critical" if score >= 95 else "high",
                    description=f"AbuseIPDB — score de confiance d'abus: {score}/100",
                    first_seen=now,
                    last_seen=now,
                )
            )
        return threats
