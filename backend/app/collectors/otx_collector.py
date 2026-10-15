from datetime import datetime, timezone

import httpx

from app.collectors.base import BaseCollector, parse_source_datetime
from app.core.config import settings
from app.schemas.threat import ThreatInput

INDICATOR_TYPE_MAP = {
    "IPv4": "ip",
    "IPv6": "ip",
    "domain": "domain",
    "hostname": "domain",
    "URL": "url",
    "URI": "url",
    "CVE": "cve",
    "FileHash-MD5": "hash",
    "FileHash-SHA1": "hash",
    "FileHash-SHA256": "hash",
}


class OTXCollector(BaseCollector):
    """Collecteur des indicateurs (IOCs) des pulses AlienVault OTX suivies.

    Nécessite OTX_API_KEY (compte gratuit sur otx.alienvault.com).
    """

    name = "otx"
    endpoint = "https://otx.alienvault.com/api/v1/pulses/subscribed"

    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        if not settings.otx_api_key:
            raise ValueError("OTX_API_KEY n'est pas configurée")

        headers = {"X-OTX-API-KEY": settings.otx_api_key}
        params = {"limit": 5}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.endpoint, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        now = datetime.now(timezone.utc)
        threats: list[ThreatInput] = []
        for pulse in payload.get("results", []):
            pulse_name = pulse.get("name", "Pulse OTX")
            for indicator in pulse.get("indicators", []):
                mapped_type = INDICATOR_TYPE_MAP.get(indicator.get("type", ""))
                if not mapped_type:
                    continue
                threats.append(
                    ThreatInput(
                        indicator=indicator["indicator"],
                        indicator_type=mapped_type,
                        threat_type="vulnerability" if mapped_type == "cve" else "malware",
                        source="otx",
                        severity="high",
                        description=f"AlienVault OTX — pulse « {pulse_name} »",
                        first_seen=parse_source_datetime(
                            indicator.get("created") or pulse.get("created"), now
                        ),
                        last_seen=now,
                    )
                )
                if len(threats) >= limit:
                    return threats
        return threats
