"""Add EPSS and CISA KEV enrichment fields

Revision ID: c7a9e2d14f63
Revises: 8f2a1c6d4b90
Create Date: 2026-10-11 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7a9e2d14f63"
down_revision: Union[str, Sequence[str], None] = "8f2a1c6d4b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("threats", sa.Column("epss_score", sa.Float(), nullable=True))
    op.add_column("threats", sa.Column("epss_percentile", sa.Float(), nullable=True))
    op.add_column("threats", sa.Column("epss_updated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "threats",
        sa.Column("known_exploited", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("threats", sa.Column("kev_date_added", sa.Date(), nullable=True))
    op.add_column("threats", sa.Column("kev_due_date", sa.Date(), nullable=True))
    op.add_column("threats", sa.Column("kev_required_action", sa.Text(), nullable=True))
    op.add_column("threats", sa.Column("kev_ransomware_use", sa.String(length=32), nullable=True))
    op.create_index(
        op.f("ix_threats_known_exploited"), "threats", ["known_exploited"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_threats_known_exploited"), table_name="threats")
    op.drop_column("threats", "kev_ransomware_use")
    op.drop_column("threats", "kev_required_action")
    op.drop_column("threats", "kev_due_date")
    op.drop_column("threats", "kev_date_added")
    op.drop_column("threats", "known_exploited")
    op.drop_column("threats", "epss_updated_at")
    op.drop_column("threats", "epss_percentile")
    op.drop_column("threats", "epss_score")
