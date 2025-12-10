"""Add email provider settings table

Revision ID: 002_email_provider
Revises: 001_initial_migration
Create Date: 2025-12-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create email_provider_settings table
    op.create_table(
        'email_provider_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('provider_type', sa.String(), nullable=False),
        sa.Column('from_name', sa.String(), nullable=False),
        sa.Column('from_email', sa.String(), nullable=False),
        sa.Column('smtp_host', sa.String(), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True),
        sa.Column('smtp_username', sa.String(), nullable=True),
        sa.Column('smtp_password_encrypted', sa.String(), nullable=True),
        sa.Column('use_tls', sa.Boolean(), default=True),
        sa.Column('use_ssl', sa.Boolean(), default=False),
        sa.Column('sendgrid_api_key_encrypted', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table('email_provider_settings')
