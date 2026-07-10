"""Add campaign_id and step_index to sending_logs for email thread anchor lookups.

Revision ID: 013_add_threading_columns
Revises: 012_production_safety_layer
Create Date: 2026-07-10
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '013_add_threading_columns'
down_revision = '012_production_safety_layer'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add campaign_id so we can query the original step-1 message_id for threading
    op.add_column(
        'sending_logs',
        sa.Column('campaign_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_sending_logs_campaign_id', 'sending_logs', ['campaign_id'])

    # Add step_index so we can distinguish the root email (step 1) from follow-ups
    op.add_column(
        'sending_logs',
        sa.Column('step_index', sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_index('ix_sending_logs_campaign_id', table_name='sending_logs')
    op.drop_column('sending_logs', 'campaign_id')
    op.drop_column('sending_logs', 'step_index')
