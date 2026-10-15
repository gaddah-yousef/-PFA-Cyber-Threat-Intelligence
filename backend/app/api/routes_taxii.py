import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.database import get_db
from app.models.threat import Threat
from app.services.intelligence_service import build_stix_bundle

TAXII_MEDIA_TYPE = "application/taxii+json;version=2.1"
STIX_MEDIA_TYPE = "application/stix+json;version=2.1"
COLLECTION_ID = "c42f1f5b-821d-5f48-9ca8-ae7f58a55c10"

discovery_router = APIRouter(tags=["TAXII 2.1"])
router = APIRouter(prefix="/api/taxii2", tags=["TAXII 2.1"])
DbSession = Annotated[Session, Depends(get_db)]


def _taxii(payload: dict) -> Response:
    return Response(
        content=json.dumps(payload, ensure_ascii=False),
        media_type=TAXII_MEDIA_TYPE,
    )


def _collection() -> dict:
    return {
        "id": COLLECTION_ID,
        "title": "Sentinel PME Threat Intelligence",
        "description": "Indicateurs normalisés et priorisés par Sentinel PME.",
        "can_read": True,
        "can_write": False,
        "media_types": [STIX_MEDIA_TYPE],
    }


@discovery_router.get("/taxii2/")
def discovery() -> Response:
    return _taxii(
        {
            "title": "Sentinel PME TAXII 2.1",
            "description": "Service TAXII 2.1 en lecture seule.",
            "default": "/api/taxii2/",
            "api_roots": ["/api/taxii2/"],
        }
    )


@router.get("/")
def api_root(_current_user: CurrentUser) -> Response:
    return _taxii(
        {
            "title": "Sentinel PME",
            "description": "API Root CTI authentifiée en lecture seule.",
            "versions": [TAXII_MEDIA_TYPE],
            "max_content_length": 10_485_760,
        }
    )


@router.get("/collections/")
def collections(_current_user: CurrentUser) -> Response:
    return _taxii({"collections": [_collection()]})


@router.get("/collections/{collection_id}/")
def collection(collection_id: str, _current_user: CurrentUser) -> Response:
    if collection_id != COLLECTION_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection introuvable")
    return _taxii(_collection())


@router.get("/collections/{collection_id}/objects/")
def collection_objects(
    collection_id: str,
    db: DbSession,
    _current_user: CurrentUser,
    limit: int = Query(500, ge=1, le=5000),
) -> Response:
    if collection_id != COLLECTION_ID:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection introuvable")
    threats = list(db.scalars(select(Threat).order_by(Threat.last_seen.desc()).limit(limit)).all())
    objects = build_stix_bundle(threats)["objects"]
    return _taxii({"more": False, "objects": objects})
