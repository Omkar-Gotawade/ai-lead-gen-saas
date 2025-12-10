"""add_title_industry_phone_to_leads

Revision ID: 2bacbfd32c06
Revises: 005
Create Date: 2025-12-10 11:25:12.400621

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bacbfd32c06'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add title, industry, and phone columns to leads table
    op.add_column('leads', sa.Column('title', sa.String(length=255), nullable=True))
    op.add_column('leads', sa.Column('industry', sa.String(length=255), nullable=True))
    op.add_column('leads', sa.Column('phone', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove title, industry, and phone columns from leads table
    op.drop_column('leads', 'phone')
    op.drop_column('leads', 'industry')
    op.drop_column('leads', 'title')
