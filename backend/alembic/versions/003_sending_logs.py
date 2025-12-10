"""Add sending logs table

Revision ID: 003_sending_logs
Revises: 002_email_provider
Create Date: 2025-12-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create sending_logs table
    op.create_table(
        'sending_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('provider_type', sa.String(), nullable=False),
        sa.Column('to_email', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('sending_logs')
