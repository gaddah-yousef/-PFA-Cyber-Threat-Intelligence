"""Persist the SME targeting context used by risk scoring.

Revision ID: d4f6027a9b31
Revises: c7a9e2d14f63
Create Date: 2026-10-15 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4f6027a9b31"
down_revision: Union[str, Sequence[str], None] = "c7a9e2d14f63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "threats",
        sa.Column("targets_smes", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_index(
        op.f("ix_threats_targets_smes"), "threats", ["targets_smes"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_threats_targets_smes"), table_name="threats")
    op.drop_column("threats", "targets_smes")
