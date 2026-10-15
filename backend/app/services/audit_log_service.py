from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record_audit_log(
    db: Session,
    actor: User,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    details: str | None = None,
) -> AuditLog:
    """Enregistre une entrée d'audit. Best-effort : une erreur ici ne doit
    jamais faire échouer l'action métier qu'elle journalise."""

    log = AuditLog(
        actor_email=actor.email,
        actor_role=actor.role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    )
    db.add(log)
    db.commit()
    return log
