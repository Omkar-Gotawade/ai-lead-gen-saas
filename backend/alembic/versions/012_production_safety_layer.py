"""Production safety layer: DNC canonical fields, send reliability fields, duplicate lead constraint.

Revision ID: 012_production_safety_layer
Revises: 011_add_user_full_name
Create Date: 2026-03-31
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_production_safety_layer'
down_revision = ('009_message_id', '011_research_notes')
branch_labels = None
depends_on = None


def upgrade() -> None:
    # leads: canonical DNC fields
    op.add_column('leads', sa.Column('is_do_not_contact', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('leads', sa.Column('dnc_reason', sa.String(length=255), nullable=True))
    op.add_column('leads', sa.Column('dnc_at', sa.DateTime(), nullable=True))
    op.create_index('ix_leads_is_do_not_contact', 'leads', ['is_do_not_contact'])

    # sending_logs: safety bookkeeping
    op.add_column('sending_logs', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('sending_logs', sa.Column('failed_at', sa.DateTime(), nullable=True))
    op.add_column('sending_logs', sa.Column('sent_at', sa.DateTime(), nullable=True))

    # leads duplicate protection per org/user
    op.create_unique_constraint('uq_leads_org_email', 'leads', ['org_id', 'email'])


def downgrade() -> None:
    op.drop_constraint('uq_leads_org_email', 'leads', type_='unique')

    op.drop_column('sending_logs', 'sent_at')
    op.drop_column('sending_logs', 'failed_at')
    op.drop_column('sending_logs', 'retry_count')

    op.drop_index('ix_leads_is_do_not_contact', table_name='leads')
    op.drop_column('leads', 'dnc_at')
    op.drop_column('leads', 'dnc_reason')
    op.drop_column('leads', 'is_do_not_contact')
