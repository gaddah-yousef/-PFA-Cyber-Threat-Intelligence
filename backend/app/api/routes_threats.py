from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_roles
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.threat import Threat
from app.models.user import UserRole
from app.schemas.threat import (
    RiskBreakdown,
    RiskLevel,
    ThreatInput,
    ThreatManualInput,
    ThreatRead,
    ThreatSource,
)
from app.services.threat_service import analyze_and_save_threat

router = APIRouter(prefix="/api/threats", tags=["Threats"])
DbSession = Annotated[Session, Depends(get_db)]
CanWrite = Depends(require_roles(UserRole.admin, UserRole.analyst))


@router.get("", response_model=list[ThreatRead])
def list_threats(
    db: DbSession,
    response: Response,
    _current_user: CurrentUser,
    risk_level: str | None = None,
    threat_type: str | None = None,
    source: str | None = None,
    search: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[Threat]:
    query = select(Threat)
    if risk_level:
        query = query.where(Threat.risk_level == risk_level)
    if threat_type:
        query = query.where(Threat.threat_type == threat_type)
    if source:
        query = query.where(Threat.source == source)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(
            or_(Threat.indicator.ilike(pattern), Threat.description.ilike(pattern))
        )

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    response.headers["X-Total-Count"] = str(total)

    query = query.order_by(Threat.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(query).all())


@router.get("/critical", response_model=list[ThreatRead])
def critical_threats(db: DbSession, _current_user: CurrentUser) -> list[Threat]:
    query = select(Threat).where(Threat.risk_score >= 90).order_by(Threat.created_at.desc())
    return list(db.scalars(query).all())


@router.get("/{threat_id}", response_model=ThreatRead)
def get_threat(threat_id: str, db: DbSession, _current_user: CurrentUser) -> Threat:
    threat = db.get(Threat, threat_id)
    if not threat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menace introuvable")
    return threat


@router.get("/{threat_id}/explain", response_model=RiskBreakdown)
def explain_threat_score(threat_id: str, db: DbSession, _current_user: CurrentUser) -> RiskBreakdown:
    """Détaille le calcul du score de risque (facteur par facteur) pour une
    menace donnée, afin que le score reste explicable face à un analyste."""

    threat = db.get(Threat, threat_id)
    if not threat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menace introuvable")
    return RiskBreakdown(
        score=threat.risk_score,
        level=RiskLevel(threat.risk_level),
        factors=threat.score_factors or {},
    )


@router.post(
    "/analyze",
    response_model=ThreatRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[CanWrite],
)
@limiter.limit("30/minute")
def analyze_threat(request: Request, payload: ThreatInput, db: DbSession) -> Threat:
    return analyze_and_save_threat(db, payload)


@router.post(
    "/manual",
    response_model=ThreatRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[CanWrite],
)
@limiter.limit("30/minute")
def create_manual_threat(request: Request, payload: ThreatManualInput, db: DbSession) -> Threat:
    manual_payload = payload.model_copy(update={"source": ThreatSource.manual})
    return analyze_and_save_threat(db, manual_payload)
