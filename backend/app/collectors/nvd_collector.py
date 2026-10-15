from datetime import datetime, timedelta, timezone

import httpx

from app.collectors.base import BaseCollector
from app.core.config import settings
from app.schemas.threat import ThreatInput


class NVDCollector(BaseCollector):
    name = "nvd"
    endpoint = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    recent_window_days = 30

    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        headers = {"apiKey": settings.nvd_api_key} if settings.nvd_api_key else {}
        page_size = min(limit, 100)
        now = datetime.now(timezone.utc)
        params = {
            "resultsPerPage": page_size,
            "pubStartDate": (now - timedelta(days=self.recent_window_days))
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "pubEndDate": now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(self.endpoint, params=params, headers=headers)
            response.raise_for_status()
            first_payload = response.json()
            start_index = max(first_payload.get("totalResults", 0) - page_size, 0)
            if start_index:
                params["startIndex"] = start_index
                response = await client.get(self.endpoint, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()
            else:
                payload = first_payload

        threats: list[ThreatInput] = []
        vulnerabilities = sorted(
            payload.get("vulnerabilities", []),
            key=lambda entry: entry.get("cve", {}).get("published", ""),
            reverse=True,
        )
        for entry in vulnerabilities[:limit]:
            cve = entry.get("cve", {})
            descriptions = cve.get("descriptions", [])
            description = next(
                (item.get("value", "") for item in descriptions if item.get("lang") == "en"),
                "Vulnérabilité publiée dans la NVD.",
            )
            published = datetime.fromisoformat(cve["published"].replace("Z", "+00:00"))
            metrics = cve.get("metrics", {})
            cvss_data = (
                metrics.get("cvssMetricV40")
                or metrics.get("cvssMetricV31")
                or metrics.get("cvssMetricV30")
                or [{}]
            )[0]
            base_score = cvss_data.get("cvssData", {}).get("baseScore", 0)
            severity = "critical" if base_score >= 9 else "high" if base_score >= 7 else "medium"
            threats.append(
                ThreatInput(
                    indicator=cve["id"],
                    indicator_type="cve",
                    threat_type="vulnerability",
                    source="nvd",
                    severity=severity,
                    description=description[:4000],
                    cvss_score=base_score,
                    cve_configurations=cve.get("configurations") or [],
                    first_seen=published,
                    last_seen=datetime.now(timezone.utc),
                )
            )
        return threats
