from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.asset import Asset, Software
from app.models.asset_vulnerability import AssetVulnerability
from app.schemas.asset import AssetCreate, AssetResponse, AssetUpdate, SoftwareCreate


def asset_query():
    return select(Asset).options(selectinload(Asset.software))


def get_asset_or_none(db: Session, asset_id: str) -> Asset | None:
    return db.scalar(asset_query().where(Asset.id == asset_id))


def to_asset_response(db: Session, asset: Asset) -> AssetResponse:
    counts = dict(
        db.execute(
            select(AssetVulnerability.matching_status, func.count(AssetVulnerability.id))
            .where(AssetVulnerability.asset_id == asset.id)
            .group_by(AssetVulnerability.matching_status)
        ).all()
    )
    return AssetResponse(
        id=asset.id,
        hostname=asset.hostname,
        ip_address=asset.ip_address,
        asset_type=asset.asset_type,
        operating_system=asset.operating_system,
        environment=asset.environment,
        criticality=asset.criticality,
        internet_exposed=asset.internet_exposed,
        owner=asset.owner,
        description=asset.description,
        software_count=len(asset.software),
        confirmed_vulnerabilities=counts.get("confirmed", 0),
        potential_vulnerabilities=counts.get("potential", 0),
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


def build_asset(payload: AssetCreate) -> Asset:
    return Asset(**payload.model_dump(mode="json"))


def apply_asset_update(asset: Asset, payload: AssetUpdate) -> None:
    for key, value in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(asset, key, value)


def add_software(db: Session, asset: Asset, payload: SoftwareCreate) -> Software:
    duplicate = db.scalar(
        select(Software).where(
            Software.asset_id == asset.id,
            func.lower(Software.name) == payload.name.lower(),
            Software.version == payload.version,
            Software.cpe == payload.cpe,
        )
    )
    if duplicate:
        raise IntegrityError("duplicate software", params=None, orig=ValueError("duplicate"))
    software = Software(asset_id=asset.id, **payload.model_dump())
    db.add(software)
    db.flush()
    return software
