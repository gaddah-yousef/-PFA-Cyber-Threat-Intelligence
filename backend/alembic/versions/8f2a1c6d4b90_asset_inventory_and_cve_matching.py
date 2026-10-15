"""Asset inventory, software inventory and CVE matching

Revision ID: 8f2a1c6d4b90
Revises: 3d41050f4232
Create Date: 2026-10-10 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f2a1c6d4b90"
down_revision: Union[str, Sequence[str], None] = "3d41050f4232"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("threats", sa.Column("cvss_score", sa.Float(), nullable=True))
    op.add_column("threats", sa.Column("cve_configurations", sa.JSON(), nullable=True))

    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("hostname", sa.String(length=253), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("asset_type", sa.String(length=32), nullable=False),
        sa.Column("operating_system", sa.String(length=255), nullable=False),
        sa.Column("environment", sa.String(length=16), nullable=False),
        sa.Column("criticality", sa.String(length=16), nullable=False),
        sa.Column("internet_exposed", sa.Boolean(), nullable=False),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hostname"),
    )
    for column in ("hostname", "ip_address", "asset_type", "environment", "criticality", "internet_exposed"):
        op.create_index(op.f(f"ix_assets_{column}"), "assets", [column], unique=column == "hostname")

    op.create_table(
        "software",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("version", sa.String(length=128), nullable=False),
        sa.Column("cpe", sa.String(length=1024), nullable=True),
        sa.Column("purl", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "name", "version", "cpe", name="uq_software_asset_name_version_cpe"),
    )
    for column in ("asset_id", "name", "vendor", "version", "cpe"):
        op.create_index(op.f(f"ix_software_{column}"), "software", [column], unique=False)

    op.create_table(
        "asset_vulnerabilities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=False),
        sa.Column("software_id", sa.String(length=36), nullable=False),
        sa.Column("threat_id", sa.String(length=36), nullable=False),
        sa.Column("matching_status", sa.String(length=16), nullable=False),
        sa.Column("matching_reason", sa.Text(), nullable=False),
        sa.Column("matching_evidence", sa.JSON(), nullable=False),
        sa.Column("first_detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remediation_status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["software_id"], ["software.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["threat_id"], ["threats.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_id", "software_id", "threat_id", name="uq_asset_vulnerability_match"),
    )
    for column in ("asset_id", "software_id", "threat_id", "matching_status", "remediation_status"):
        op.create_index(op.f(f"ix_asset_vulnerabilities_{column}"), "asset_vulnerabilities", [column], unique=False)


def downgrade() -> None:
    for column in ("remediation_status", "matching_status", "threat_id", "software_id", "asset_id"):
        op.drop_index(op.f(f"ix_asset_vulnerabilities_{column}"), table_name="asset_vulnerabilities")
    op.drop_table("asset_vulnerabilities")
    for column in ("cpe", "version", "vendor", "name", "asset_id"):
        op.drop_index(op.f(f"ix_software_{column}"), table_name="software")
    op.drop_table("software")
    for column in ("internet_exposed", "criticality", "environment", "asset_type", "ip_address", "hostname"):
        op.drop_index(op.f(f"ix_assets_{column}"), table_name="assets")
    op.drop_table("assets")
    op.drop_column("threats", "cve_configurations")
    op.drop_column("threats", "cvss_score")
