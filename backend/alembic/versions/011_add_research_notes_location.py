"""Add research_notes and location fields to leads

Revision ID: 011_research_notes
Revises: 010_ai_personalization
Create Date: 2026-01-04 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_research_notes'
down_revision = '010_ai_personalization'
branch_labels = None
depends_on = None


def upgrade():
    """Add research_notes and location fields for better email personalization."""
    # Add location field
    op.add_column('leads', sa.Column('location', sa.String(255), nullable=True))
    
    # Add research_notes field (Text type for longer content)
    op.add_column('leads', sa.Column('research_notes', sa.Text(), nullable=True))


def downgrade():
    """Remove research_notes and location fields."""
    op.drop_column('leads', 'research_notes')
    op.drop_column('leads', 'location')
