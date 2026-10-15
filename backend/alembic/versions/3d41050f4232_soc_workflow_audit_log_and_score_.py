"""SOC workflow on alerts, audit log, explainable score factors

Revision ID: 3d41050f4232
Revises: e73861556618
Create Date: 2026-10-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d41050f4232'
down_revision: Union[str, Sequence[str], None] = 'e73861556618'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Workflow SOC léger sur les alertes (statut, assignation, notes).
    op.add_column('alerts', sa.Column('status', sa.String(length=16), nullable=False, server_default='new'))
    op.add_column('alerts', sa.Column('assigned_to', sa.String(length=255), nullable=True))
    op.add_column('alerts', sa.Column('resolution_notes', sa.Text(), nullable=True))
    op.add_column(
        'alerts',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_alerts_status'), 'alerts', ['status'], unique=False)

    # Les alertes déjà acquittées avant la migration sont considérées comme
    # résolues, pour rester cohérentes avec le nouveau workflow. Passe par une
    # construction SQLAlchemy (plutôt qu'une chaîne SQL brute) pour que le
    # littéral booléen reste correct aussi bien sur SQLite que PostgreSQL.
    alerts_table = sa.table(
        'alerts',
        sa.column('status', sa.String),
        sa.column('acknowledged', sa.Boolean),
    )
    op.execute(
        alerts_table.update()
        .where(alerts_table.c.acknowledged == True)  # noqa: E712
        .values(status='resolved')
    )

    # Score de risque explicable : les facteurs de calcul sont persistés.
    op.add_column('threats', sa.Column('score_factors', sa.JSON(), nullable=True))

    # Journal d'audit des actions sensibles.
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('actor_email', sa.String(length=255), nullable=False),
        sa.Column('actor_role', sa.String(length=16), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=True),
        sa.Column('target_id', sa.String(length=64), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_actor_email'), 'audit_logs', ['actor_email'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_actor_email'), table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_column('threats', 'score_factors')

    op.drop_index(op.f('ix_alerts_status'), table_name='alerts')
    op.drop_column('alerts', 'updated_at')
    op.drop_column('alerts', 'resolution_notes')
    op.drop_column('alerts', 'assigned_to')
    op.drop_column('alerts', 'status')
