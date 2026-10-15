from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.threat import Threat
from app.services.notification_service import send_alert_notifications


def create_alert_for_threat(db: Session, threat: Threat) -> Alert | None:
    if threat.risk_score < 70:
        return None

    existing = db.scalar(select(Alert).where(Alert.threat_id == threat.id))
    if existing:
        return existing

    level = "critical" if threat.risk_score >= 90 else "high"
    alert = Alert(
        threat_id=threat.id,
        level=level,
        title=f"Menace {level} détectée",
        message=f"{threat.indicator} — score {threat.risk_score}/100. {threat.recommended_action}",
    )
    db.add(alert)
    db.flush()
    send_alert_notifications(alert, threat)
    return alert
