"""Initial migration - create users and leads tables

Revision ID: 001
Revises: 
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create leads table
    op.create_table(
        'leads',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', UUID(as_uuid=True), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('enriched_data', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_leads_email', 'leads', ['email'])
    op.create_index('ix_leads_org_id', 'leads', ['org_id'])


def downgrade() -> None:
    op.drop_index('ix_leads_org_id', 'leads')
    op.drop_index('ix_leads_email', 'leads')
    op.drop_table('leads')
    
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
