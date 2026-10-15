import csv
import io
import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_roles
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.asset import Asset, Software
from app.models.asset_vulnerability import AssetVulnerability
from app.models.user import User, UserRole
from app.schemas.asset import (
    AssetCreate,
    AssetImportReport,
    AssetResponse,
    AssetStats,
    AssetUpdate,
    AssetVulnerabilityResponse,
    ImportRowError,
    SoftwareCreate,
    SoftwareResponse,
)
from app.services.asset_service import (
    add_software,
    apply_asset_update,
    asset_query,
    build_asset,
    get_asset_or_none,
    to_asset_response,
)
from app.services.audit_log_service import record_audit_log
from app.services.vulnerability_matching import refresh_asset_matches

router = APIRouter(prefix="/api/assets", tags=["Assets"])
DbSession = Annotated[Session, Depends(get_db)]
CanWrite = Annotated[User, Depends(require_roles(UserRole.admin, UserRole.analyst))]
MAX_CSV_BYTES = 1024 * 1024
MAX_CSV_ROWS = 500
CSV_FIELDS = {
    "hostname", "ip_address", "asset_type", "operating_system", "environment",
    "criticality", "internet_exposed", "owner", "description",
}


def _asset_or_404(db: Session, asset_id: str) -> Asset:
    asset = get_asset_or_none(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Actif introuvable")
    return asset


@router.get("", response_model=list[AssetResponse])
def list_assets(
    db: DbSession,
    response: Response,
    _current_user: CurrentUser,
    search: str | None = None,
    asset_type: str | None = None,
    environment: str | None = None,
    criticality: str | None = None,
    internet_exposed: bool | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[AssetResponse]:
    query = asset_query()
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(or_(Asset.hostname.ilike(pattern), Asset.ip_address.ilike(pattern)))
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
    if environment:
        query = query.where(Asset.environment == environment)
    if criticality:
        query = query.where(Asset.criticality == criticality)
    if internet_exposed is not None:
        query = query.where(Asset.internet_exposed == internet_exposed)
    total = db.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    response.headers["X-Total-Count"] = str(total)
    assets = db.scalars(query.order_by(Asset.created_at.desc()).offset(offset).limit(limit)).all()
    return [to_asset_response(db, asset) for asset in assets]


@router.get("/stats", response_model=AssetStats)
def asset_stats(db: DbSession, _current_user: CurrentUser) -> AssetStats:
    total = db.scalar(select(func.count(Asset.id))) or 0
    critical = db.scalar(select(func.count(Asset.id)).where(Asset.criticality == "critical")) or 0
    exposed = db.scalar(select(func.count(Asset.id)).where(Asset.internet_exposed.is_(True))) or 0
    confirmed = db.scalar(select(func.count(func.distinct(AssetVulnerability.asset_id))).where(AssetVulnerability.matching_status == "confirmed")) or 0
    potential = db.scalar(select(func.count(func.distinct(AssetVulnerability.asset_id))).where(AssetVulnerability.matching_status == "potential")) or 0
    return AssetStats(total=total, critical=critical, internet_exposed=exposed, with_confirmed_vulnerabilities=confirmed, requiring_verification=potential)


@router.post("/import", response_model=AssetImportReport)
@limiter.limit("5/minute")
async def import_assets(request: Request, db: DbSession, actor: CanWrite, file: UploadFile = File(...)) -> AssetImportReport:
    if file.content_type not in {"text/csv", "application/csv", "application/vnd.ms-excel"}:
        raise HTTPException(status_code=415, detail="Le fichier doit être un CSV")
    raw = await file.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="Le fichier CSV dépasse 1 Mio")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail="Le fichier doit être encodé en UTF-8") from exc
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not CSV_FIELDS.issubset(set(reader.fieldnames)):
        raise HTTPException(status_code=422, detail="En-têtes CSV manquants ou invalides")
    created = skipped = 0
    errors: list[ImportRowError] = []
    for index, row in enumerate(reader, start=2):
        if index > MAX_CSV_ROWS + 1:
            raise HTTPException(status_code=413, detail="Le CSV dépasse 500 lignes")
        try:
            payload = AssetCreate.model_validate({key: row.get(key) or None for key in CSV_FIELDS})
            if db.scalar(select(Asset.id).where(func.lower(Asset.hostname) == payload.hostname.lower())):
                skipped += 1
                continue
            # Un SAVEPOINT isole une ligne invalide sans annuler les lignes valides
            # déjà préparées dans la même transaction d'import.
            with db.begin_nested():
                db.add(build_asset(payload))
                db.flush()
            created += 1
        except (ValidationError, IntegrityError, ValueError) as exc:
            errors.append(ImportRowError(row=index, message=str(exc).splitlines()[0][:300]))
    db.commit()
    record_audit_log(db, actor, "asset.import", "asset", details=json.dumps({"created": created, "skipped": skipped, "errors": len(errors)}))
    return AssetImportReport(created=created, skipped=skipped, error_count=len(errors), errors=errors)


@router.post("", response_model=AssetResponse, status_code=201)
@limiter.limit("30/minute")
def create_asset(request: Request, payload: AssetCreate, db: DbSession, actor: CanWrite) -> AssetResponse:
    asset = build_asset(payload)
    db.add(asset)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce hostname existe déjà") from exc
    db.refresh(asset)
    record_audit_log(db, actor, "asset.create", "asset", asset.id, asset.hostname)
    return to_asset_response(db, asset)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: str, db: DbSession, _current_user: CurrentUser) -> AssetResponse:
    return to_asset_response(db, _asset_or_404(db, asset_id))


@router.patch("/{asset_id}", response_model=AssetResponse)
@limiter.limit("30/minute")
def update_asset(request: Request, asset_id: str, payload: AssetUpdate, db: DbSession, actor: CanWrite) -> AssetResponse:
    asset = _asset_or_404(db, asset_id)
    apply_asset_update(asset, payload)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce hostname existe déjà") from exc
    db.refresh(asset)
    record_audit_log(db, actor, "asset.update", "asset", asset.id, json.dumps(payload.model_dump(exclude_unset=True, mode="json")))
    return to_asset_response(db, asset)


@router.delete("/{asset_id}", status_code=204)
@limiter.limit("30/minute")
def delete_asset(request: Request, asset_id: str, db: DbSession, actor: CanWrite) -> Response:
    asset = _asset_or_404(db, asset_id)
    asset_id_value, hostname = asset.id, asset.hostname
    db.delete(asset)
    db.commit()
    record_audit_log(db, actor, "asset.delete", "asset", asset_id_value, hostname)
    return Response(status_code=204)


@router.get("/{asset_id}/software", response_model=list[SoftwareResponse])
def list_software(asset_id: str, db: DbSession, _current_user: CurrentUser) -> list[Software]:
    _asset_or_404(db, asset_id)
    return list(db.scalars(select(Software).where(Software.asset_id == asset_id).order_by(Software.name)).all())


@router.post("/{asset_id}/software", response_model=SoftwareResponse, status_code=201)
@limiter.limit("30/minute")
def create_software(request: Request, asset_id: str, payload: SoftwareCreate, db: DbSession, actor: CanWrite) -> Software:
    asset = _asset_or_404(db, asset_id)
    try:
        software = add_software(db, asset, payload)
        refresh_asset_matches(db, asset)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ce logiciel existe déjà sur cet actif") from exc
    db.refresh(software)
    record_audit_log(db, actor, "software.create", "software", software.id, asset_id)
    return software


@router.get("/{asset_id}/vulnerabilities", response_model=list[AssetVulnerabilityResponse])
def list_vulnerabilities(asset_id: str, db: DbSession, _current_user: CurrentUser) -> list[AssetVulnerabilityResponse]:
    asset = _asset_or_404(db, asset_id)
    matches = refresh_asset_matches(db, asset)
    db.commit()
    result = []
    for match in matches:
        result.append(AssetVulnerabilityResponse(
            id=match.id, asset_id=match.asset_id, software_id=match.software_id,
            threat_id=match.threat_id, cve_id=match.threat.indicator,
            software_name=match.software.name, software_version=match.software.version,
            matching_status=match.matching_status, matching_reason=match.matching_reason,
            matching_evidence=match.matching_evidence or {}, remediation_status=match.remediation_status,
            risk_score=match.threat.risk_score, risk_level=match.threat.risk_level,
            first_detected_at=match.first_detected_at, last_checked_at=match.last_checked_at,
        ))
    return result
