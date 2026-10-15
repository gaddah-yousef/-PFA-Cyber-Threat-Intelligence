from datetime import datetime, timezone
from ipaddress import ip_address
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    hostname: Mapped[str] = mapped_column(String(253), unique=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(32), index=True)
    operating_system: Mapped[str] = mapped_column(String(255))
    environment: Mapped[str] = mapped_column(String(16), index=True)
    criticality: Mapped[str] = mapped_column(String(16), index=True)
    internet_exposed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    software = relationship(
        "Software", back_populates="asset", cascade="all, delete-orphan", lazy="selectin"
    )
    vulnerabilities = relationship(
        "AssetVulnerability", back_populates="asset", cascade="all, delete-orphan"
    )

    @validates("ip_address")
    def validate_ip_address(self, _key: str, value: str | None) -> str | None:
        return str(ip_address(value)) if value else None


class Software(Base):
    __tablename__ = "software"
    __table_args__ = (
        UniqueConstraint("asset_id", "name", "version", "cpe", name="uq_software_asset_name_version_cpe"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assets.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    version: Mapped[str] = mapped_column(String(128), index=True)
    cpe: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)
    purl: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    asset = relationship("Asset", back_populates="software")
    vulnerabilities = relationship(
        "AssetVulnerability", back_populates="software", cascade="all, delete-orphan"
    )
