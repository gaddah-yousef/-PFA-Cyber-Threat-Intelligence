from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import UserRole
from app.schemas.audit import AuditLogRead

router = APIRouter(prefix="/api/audit-logs", tags=["Audit"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[AuditLogRead],
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def list_audit_logs(db: DbSession, limit: int = Query(100, ge=1, le=500)) -> list[AuditLog]:
    """Journal d'audit des actions sensibles (connexion, gestion des comptes,
    traitement des alertes, déclenchement des collecteurs). Réservé à
    l'administrateur, conformément aux exigences de traçabilité du cahier
    des charges."""

    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    return list(db.scalars(query).all())
