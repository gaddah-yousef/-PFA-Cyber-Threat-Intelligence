from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Date, JSON, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Threat(Base):
    __tablename__ = "threats"
    __table_args__ = (
        UniqueConstraint("indicator", "source", name="uq_threats_indicator_source"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    indicator: Mapped[str] = mapped_column(String(2048), index=True)
    indicator_type: Mapped[str] = mapped_column(String(32), index=True)
    threat_type: Mapped[str] = mapped_column(String(32), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(16), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    recommended_action: Mapped[str] = mapped_column(Text)
    score_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cve_configurations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    epss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    epss_percentile: Mapped[float | None] = mapped_column(Float, nullable=True)
    epss_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    known_exploited: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    targets_smes: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    kev_date_added: Mapped[date | None] = mapped_column(Date, nullable=True)
    kev_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    kev_required_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    kev_ransomware_use: Mapped[str | None] = mapped_column(String(32), nullable=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    alerts = relationship("Alert", back_populates="threat", cascade="all, delete-orphan")
    asset_vulnerabilities = relationship(
        "AssetVulnerability", back_populates="threat", cascade="all, delete-orphan"
    )
