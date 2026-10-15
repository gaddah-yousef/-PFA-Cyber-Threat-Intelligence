from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IndicatorType(str, Enum):
    ip = "ip"
    domain = "domain"
    url = "url"
    cve = "cve"
    hash = "hash"


class ThreatType(str, Enum):
    phishing = "phishing"
    malware = "malware"
    ransomware = "ransomware"
    brute_force = "brute_force"
    vulnerability = "vulnerability"
    suspicious_ip = "suspicious_ip"
    unknown = "unknown"


class ThreatSource(str, Enum):
    manual = "manual"
    urlhaus = "urlhaus"
    nvd = "nvd"
    abuseipdb = "abuseipdb"
    otx = "otx"
    sample = "sample"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ThreatInput(BaseModel):
    indicator: str = Field(min_length=2, max_length=2048)
    indicator_type: IndicatorType
    threat_type: ThreatType = ThreatType.unknown
    source: ThreatSource = ThreatSource.manual
    severity: RiskLevel = RiskLevel.medium
    description: str = Field(default="", max_length=4000)
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # None signifie que la source d'enrichissement n'a pas répondu ; False
    # signifie que le catalogue a répondu et que la CVE n'y figure pas.
    known_exploited: bool | None = None
    # None permet de distinguer une information absente d'une valeur False
    # explicitement fournie pendant une mise à jour.
    targets_smes: bool | None = None
    cvss_score: float | None = Field(default=None, ge=0, le=10)
    cve_configurations: list[dict] | None = None
    epss_score: float | None = Field(default=None, ge=0, le=1)
    epss_percentile: float | None = Field(default=None, ge=0, le=1)
    epss_updated_at: datetime | None = None
    kev_date_added: date | None = None
    kev_due_date: date | None = None
    kev_required_action: str | None = Field(default=None, max_length=4000)
    kev_ransomware_use: str | None = Field(default=None, max_length=32)

    @field_validator("indicator")
    @classmethod
    def strip_indicator(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("L'indicateur ne peut pas être vide")
        return value


class ThreatManualInput(ThreatInput):
    source: ThreatSource = ThreatSource.manual


class ThreatRead(BaseModel):
    id: str
    indicator: str
    indicator_type: IndicatorType
    threat_type: ThreatType
    source: ThreatSource
    severity: RiskLevel
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    description: str
    recommended_action: str
    cvss_score: float | None = None
    epss_score: float | None = None
    epss_percentile: float | None = None
    epss_updated_at: datetime | None = None
    known_exploited: bool = False
    targets_smes: bool = False
    kev_date_added: date | None = None
    kev_due_date: date | None = None
    kev_required_action: str | None = None
    kev_ransomware_use: str | None = None
    first_seen: datetime
    last_seen: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreatList(BaseModel):
    total: int
    items: list[ThreatRead]


class RiskBreakdown(BaseModel):
    score: int
    level: RiskLevel
    factors: dict[str, int]
