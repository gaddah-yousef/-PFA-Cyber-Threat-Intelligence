from datetime import datetime, timezone

from app.collectors.base import BaseCollector
from app.schemas.threat import ThreatInput


class SampleCollector(BaseCollector):
    name = "sample"

    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        now = datetime.now(timezone.utc)
        samples = [
            ThreatInput(
                indicator="fake-office365-login.example",
                indicator_type="domain",
                threat_type="phishing",
                source="sample",
                severity="high",
                description="Domaine imitant une page de connexion professionnelle.",
                targets_smes=True,
                first_seen=now,
                last_seen=now,
            ),
            ThreatInput(
                indicator="185.220.101.45",
                indicator_type="ip",
                threat_type="brute_force",
                source="sample",
                severity="medium",
                description="Adresse IP observée lors de tentatives répétées de connexion.",
                first_seen=now,
                last_seen=now,
            ),
            ThreatInput(
                indicator="CVE-2026-10001",
                indicator_type="cve",
                threat_type="vulnerability",
                source="sample",
                severity="critical",
                description="Vulnérabilité critique de démonstration, connue comme exploitée.",
                known_exploited=True,
                targets_smes=True,
                first_seen=now,
                last_seen=now,
            ),
            ThreatInput(
                indicator="https://download-update.example/payload.exe",
                indicator_type="url",
                threat_type="malware",
                source="sample",
                severity="high",
                description="URL de téléchargement associée à un exécutable malveillant.",
                first_seen=now,
                last_seen=now,
            ),
        ]
        return samples[:limit]
