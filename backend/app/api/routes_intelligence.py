from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.database import get_db
from app.models.threat import Threat
from app.services.intelligence_service import (
    build_misp_event,
    build_stix_bundle,
    correlate_threats,
    detect_score_anomalies,
)

router = APIRouter(prefix="/api/intelligence", tags=["Threat Intelligence"])
DbSession = Annotated[Session, Depends(get_db)]


def _latest_threats(db: Session, limit: int) -> list[Threat]:
    query = select(Threat).order_by(Threat.last_seen.desc()).limit(limit)
    return list(db.scalars(query).all())


@router.get("/export/stix")
def export_stix(
    db: DbSession,
    _current_user: CurrentUser,
    limit: int = Query(500, ge=1, le=5000),
) -> dict:
    return build_stix_bundle(_latest_threats(db, limit))


@router.get("/export/misp")
def export_misp(
    db: DbSession,
    _current_user: CurrentUser,
    limit: int = Query(500, ge=1, le=5000),
) -> dict:
    return build_misp_event(_latest_threats(db, limit))


@router.get("/correlations")
def correlations(
    db: DbSession,
    _current_user: CurrentUser,
    limit: int = Query(2000, ge=1, le=5000),
) -> list[dict]:
    return correlate_threats(_latest_threats(db, limit))


@router.get("/anomalies")
def anomalies(
    db: DbSession,
    _current_user: CurrentUser,
    limit: int = Query(2000, ge=5, le=5000),
) -> list[dict]:
    return detect_score_anomalies(_latest_threats(db, limit))
