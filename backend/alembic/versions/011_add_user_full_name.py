"""Add full_name to users

Revision ID: 011_add_user_full_name
Revises: 010_ai_personalization
Create Date: 2025-12-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_add_user_full_name'
down_revision = '010_ai_personalization'
branch_labels = None
depends_on = None


def upgrade():
    # Add full_name column to users table
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))


def downgrade():
    # Remove full_name column from users table
    op.drop_column('users', 'full_name')
