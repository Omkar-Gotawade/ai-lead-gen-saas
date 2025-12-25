"""Add AI personalization fields to sequence_steps

Revision ID: 010_ai_personalization
Revises: 009_v1_features
Create Date: 2025-12-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_ai_personalization'
down_revision = '009_v1_features'
branch_labels = None
depends_on = None


def upgrade():
    """Add AI-powered email generation fields to sequence_steps table."""
    # Add columns for AI personalization
    op.add_column('sequence_steps', sa.Column('use_ai_generation', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('sequence_steps', sa.Column('ai_tone', sa.String(), nullable=True))
    op.add_column('sequence_steps', sa.Column('ai_goal', sa.String(), nullable=True))
    op.add_column('sequence_steps', sa.Column('product_description', sa.String(), nullable=True))
    
    # Set default values for existing rows
    op.execute("""
        UPDATE sequence_steps 
        SET ai_tone = 'professional', 
            ai_goal = 'schedule a meeting'
        WHERE ai_tone IS NULL
    """)


def downgrade():
    """Remove AI personalization fields."""
    op.drop_column('sequence_steps', 'product_description')
    op.drop_column('sequence_steps', 'ai_goal')
    op.drop_column('sequence_steps', 'ai_tone')
    op.drop_column('sequence_steps', 'use_ai_generation')
