from abc import ABC, abstractmethod
from datetime import datetime, timezone

from app.schemas.threat import ThreatInput


def parse_source_datetime(value: str | None, fallback: datetime) -> datetime:
    """Convertit les horodatages ISO des sources en dates UTC cohérentes."""

    if not value:
        return fallback
    normalized = value.strip().replace(" UTC", "+00:00").replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class BaseCollector(ABC):
    name: str

    @abstractmethod
    async def collect(self, limit: int = 20) -> list[ThreatInput]:
        """Collecte et normalise au maximum ``limit`` indicateurs."""
