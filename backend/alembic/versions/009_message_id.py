"""Add message_id to sending_logs for duplicate prevention

Revision ID: 009_message_id
Revises:
Create Date: 2026-03-21
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '009_message_id'
down_revision = '008_v1_discovery'  # Adjust based on your latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add message_id column to sending_logs table"""
    op.add_column('sending_logs', sa.Column('message_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_sending_logs_message_id'), 'sending_logs', ['message_id'], unique=True)


def downgrade():
    """Remove message_id column"""
    op.drop_index(op.f('ix_sending_logs_message_id'), table_name='sending_logs')
    op.drop_column('sending_logs', 'message_id')
