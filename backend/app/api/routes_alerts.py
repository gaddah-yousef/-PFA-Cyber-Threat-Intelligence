from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_roles
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.alert import Alert
from app.models.threat import Threat
from app.models.user import UserRole
from app.schemas.alert import (
    AlertRead,
    AlertTestInput,
    AlertUpdate,
    SiemAlertPayload,
    SiemEvent,
    SiemThreatPayload,
)
from app.services.audit_log_service import record_audit_log
from app.services.siem_service import build_elastic_ecs_event, build_wazuh_event

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])
DbSession = Annotated[Session, Depends(get_db)]
CanWrite = Depends(require_roles(UserRole.admin, UserRole.analyst))

RESOLVED_STATUSES = {"resolved", "false_positive"}


def _get_alert_or_404(db: Session, alert_id: str) -> Alert:
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alerte introuvable")
    return alert


@router.get("", response_model=list[AlertRead])
def list_alerts(db: DbSession, _current_user: CurrentUser) -> list[Alert]:
    query = select(Alert).order_by(Alert.created_at.desc()).limit(100)
    return list(db.scalars(query).all())


@router.post("/test", response_model=AlertRead, status_code=status.HTTP_201_CREATED, dependencies=[CanWrite])
@limiter.limit("10/minute")
def create_test_alert(request: Request, payload: AlertTestInput, db: DbSession) -> Alert:
    level = payload.level if payload.level in {"high", "critical"} else "critical"
    alert = Alert(
        level=level,
        title="Alerte de test",
        message=payload.message,
        channel="dashboard",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}", response_model=AlertRead, dependencies=[CanWrite])
def update_alert(alert_id: str, payload: AlertUpdate, db: DbSession, current_user: CurrentUser) -> Alert:
    """Mini-workflow SOC : changer le statut, assigner un analyste, ajouter des
    notes de résolution. N'importe quel sous-ensemble de champs peut être
    envoyé (mise à jour partielle)."""

    alert = _get_alert_or_404(db, alert_id)
    data = payload.model_dump(exclude_unset=True)

    if "status" in data and data["status"] is not None:
        alert.status = data["status"].value
        if alert.status in RESOLVED_STATUSES:
            alert.acknowledged = True
    if "assigned_to" in data:
        alert.assigned_to = data["assigned_to"]
    if "resolution_notes" in data:
        alert.resolution_notes = data["resolution_notes"]

    db.commit()
    db.refresh(alert)
    record_audit_log(
        db,
        current_user,
        action="alert.update",
        target_type="alert",
        target_id=alert.id,
        details=f"status={alert.status} assigned_to={alert.assigned_to}",
    )
    return alert


@router.patch("/{alert_id}/acknowledge", response_model=AlertRead, dependencies=[CanWrite])
def acknowledge_alert(alert_id: str, db: DbSession, current_user: CurrentUser) -> Alert:
    alert = _get_alert_or_404(db, alert_id)
    alert.acknowledged = True
    alert.status = "resolved"
    db.commit()
    db.refresh(alert)
    record_audit_log(
        db, current_user, action="alert.acknowledge", target_type="alert", target_id=alert.id
    )
    return alert


@router.get("/{alert_id}/siem-event", response_model=SiemEvent)
def get_alert_siem_event(alert_id: str, db: DbSession, _current_user: CurrentUser) -> SiemEvent:
    """Expose l'alerte dans un format JSON stable, prêt à être relayé vers un
    SIEM (Wazuh/Elastic/Splunk) ou un webhook SOC externe."""

    alert = _get_alert_or_404(db, alert_id)
    threat = db.get(Threat, alert.threat_id) if alert.threat_id else None
    if threat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune menace associée à cette alerte (alerte de test)",
        )

    return SiemEvent(
        generated_at=datetime.now(timezone.utc),
        alert=SiemAlertPayload.model_validate(alert, from_attributes=True),
        threat=SiemThreatPayload.model_validate(threat, from_attributes=True),
        recommended_action=threat.recommended_action,
    )


def _get_alert_and_threat(db: Session, alert_id: str) -> tuple[Alert, Threat]:
    alert = _get_alert_or_404(db, alert_id)
    threat = db.get(Threat, alert.threat_id) if alert.threat_id else None
    if threat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune menace associée à cette alerte (alerte de test)",
        )
    return alert, threat


@router.get("/{alert_id}/siem-event/elastic")
def get_alert_elastic_event(
    alert_id: str, db: DbSession, _current_user: CurrentUser
) -> dict:
    alert, threat = _get_alert_and_threat(db, alert_id)
    return build_elastic_ecs_event(alert, threat)


@router.get("/{alert_id}/siem-event/wazuh")
def get_alert_wazuh_event(
    alert_id: str, db: DbSession, _current_user: CurrentUser
) -> dict:
    alert, threat = _get_alert_and_threat(db, alert_id)
    return build_wazuh_event(alert, threat)
