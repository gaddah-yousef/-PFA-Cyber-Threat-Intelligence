import re
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, field_validator, model_validator


class AssetType(str, Enum):
    server = "server"
    workstation = "workstation"
    network_device = "network_device"
    application = "application"
    cloud_resource = "cloud_resource"
    other = "other"


class AssetEnvironment(str, Enum):
    production = "production"
    development = "development"
    testing = "testing"


class AssetCriticality(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class MatchingStatus(str, Enum):
    confirmed = "confirmed"
    potential = "potential"
    not_affected = "not_affected"


class AssetInputBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hostname: str = Field(min_length=1, max_length=253)
    ip_address: IPvAnyAddress | None = None
    asset_type: AssetType
    operating_system: str = Field(min_length=1, max_length=255)
    environment: AssetEnvironment
    criticality: AssetCriticality
    internet_exposed: bool = False
    owner: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9._-]{0,251}[a-z0-9])?", normalized):
            raise ValueError("Le hostname contient des caractères invalides")
        return normalized

    @field_validator("operating_system")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Le système d'exploitation est obligatoire")
        return stripped

    @field_validator("owner", "description")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class AssetCreate(AssetInputBase):
    pass


class AssetUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hostname: str | None = Field(default=None, min_length=1, max_length=253)
    ip_address: IPvAnyAddress | None = None
    asset_type: AssetType | None = None
    operating_system: str | None = Field(default=None, min_length=1, max_length=255)
    environment: AssetEnvironment | None = None
    criticality: AssetCriticality | None = None
    internet_exposed: bool | None = None
    owner: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=4000)

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("Le hostname ne peut pas être nul")
        normalized = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9._-]{0,251}[a-z0-9])?", normalized):
            raise ValueError("Le hostname contient des caractères invalides")
        return normalized

    @model_validator(mode="after")
    def prevent_null_required_fields(self):
        required = {
            "asset_type", "operating_system", "environment", "criticality", "internet_exposed"
        }
        invalid = [name for name in required if name in self.model_fields_set and getattr(self, name) is None]
        if invalid:
            raise ValueError(f"Ces champs ne peuvent pas être nuls : {', '.join(invalid)}")
        return self


class AssetResponse(BaseModel):
    id: str
    hostname: str
    ip_address: IPv4Address | IPv6Address | None
    asset_type: AssetType
    operating_system: str
    environment: AssetEnvironment
    criticality: AssetCriticality
    internet_exposed: bool
    owner: str | None
    description: str | None
    software_count: int = 0
    confirmed_vulnerabilities: int = 0
    potential_vulnerabilities: int = 0
    created_at: datetime
    updated_at: datetime


class SoftwareCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    vendor: str | None = Field(default=None, max_length=255)
    version: str = Field(min_length=1, max_length=128)
    cpe: str | None = Field(default=None, max_length=1024)
    purl: str | None = Field(default=None, max_length=1024)

    @field_validator("name", "vendor", "version", "cpe", "purl")
    @classmethod
    def strip_values(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("cpe")
    @classmethod
    def validate_cpe(cls, value: str | None) -> str | None:
        if value and not re.match(r"^cpe:2\.3:[aho*\-]:", value, flags=re.IGNORECASE):
            raise ValueError("Le CPE doit utiliser le format CPE 2.3")
        return value

    @field_validator("purl")
    @classmethod
    def validate_purl(cls, value: str | None) -> str | None:
        if value and not value.startswith("pkg:"):
            raise ValueError("Le purl doit commencer par 'pkg:'")
        return value


class SoftwareResponse(BaseModel):
    id: str
    asset_id: str
    name: str
    vendor: str | None
    version: str
    cpe: str | None
    purl: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetVulnerabilityResponse(BaseModel):
    id: str
    asset_id: str
    software_id: str
    threat_id: str
    cve_id: str
    software_name: str
    software_version: str
    matching_status: MatchingStatus
    matching_reason: str
    matching_evidence: dict[str, object]
    remediation_status: str
    risk_score: int
    risk_level: str
    first_detected_at: datetime
    last_checked_at: datetime


class AssetStats(BaseModel):
    total: int
    critical: int
    internet_exposed: int
    with_confirmed_vulnerabilities: int
    requiring_verification: int


class ImportRowError(BaseModel):
    row: int
    message: str


class AssetImportReport(BaseModel):
    created: int
    skipped: int
    error_count: int
    errors: list[ImportRowError]
