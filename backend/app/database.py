from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Les imports enregistrent les tables dans les métadonnées SQLAlchemy.
    from app.models.alert import Alert  # noqa: F401
    from app.models.asset import Asset, Software  # noqa: F401
    from app.models.asset_vulnerability import AssetVulnerability  # noqa: F401
    from app.models.audit_log import AuditLog  # noqa: F401
    from app.models.threat import Threat  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
