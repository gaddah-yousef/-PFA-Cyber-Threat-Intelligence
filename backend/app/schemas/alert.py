from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AlertStatus(str, Enum):
    new = "new"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"


class AlertRead(BaseModel):
    id: str
    threat_id: str | None
    level: str
    title: str
    message: str
    channel: str
    acknowledged: bool
    status: AlertStatus
    assigned_to: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertTestInput(BaseModel):
    level: str = "critical"
    message: str = "Alerte de test : vérification du canal dashboard."


class AlertUpdate(BaseModel):
    """Mise à jour du mini-workflow SOC d'une alerte (statut, assignation, notes)."""

    status: AlertStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=255)
    resolution_notes: str | None = Field(default=None, max_length=4000)


class SiemAlertPayload(BaseModel):
    id: str
    level: str
    status: AlertStatus
    title: str
    message: str
    assigned_to: str | None
    acknowledged: bool
    created_at: datetime


class SiemThreatPayload(BaseModel):
    id: str
    indicator: str
    indicator_type: str
    threat_type: str
    source: str
    severity: str
    risk_score: int
    risk_level: str
    description: str
    first_seen: datetime
    last_seen: datetime


class SiemEvent(BaseModel):
    """Format JSON stable, exploitable par un SIEM/SOAR externe ou un webhook."""

    schema_version: str = "1.0"
    event_type: str = "sentinel_pme.threat_alert"
    generated_at: datetime
    alert: SiemAlertPayload
    threat: SiemThreatPayload
    recommended_action: str
