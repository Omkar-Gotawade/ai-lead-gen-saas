"""Add AI context columns to campaigns and is_ai_generated to sequence_steps

Revision ID: 014_campaign_ai_context
Revises: 013_add_threading_columns
Create Date: 2026-07-10 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '014_campaign_ai_context'
down_revision = '013_add_threading_columns'
branch_labels = None
depends_on = None

def upgrade():
    # Add AI context columns to campaigns
    op.add_column('campaigns', sa.Column('ai_product_name', sa.String(), nullable=True))
    op.add_column('campaigns', sa.Column('ai_product_description', sa.String(), nullable=True))
    op.add_column('campaigns', sa.Column('ai_target_audience', sa.String(), nullable=True))
    op.add_column('campaigns', sa.Column('ai_campaign_goal', sa.String(), nullable=True))
    op.add_column('campaigns', sa.Column('ai_tone', sa.String(), nullable=True))

    # Add is_ai_generated to sequence_steps
    op.add_column('sequence_steps', sa.Column('is_ai_generated', sa.Boolean(), server_default='false', nullable=False))

def downgrade():
    op.drop_column('sequence_steps', 'is_ai_generated')
    op.drop_column('campaigns', 'ai_tone')
    op.drop_column('campaigns', 'ai_campaign_goal')
    op.drop_column('campaigns', 'ai_target_audience')
    op.drop_column('campaigns', 'ai_product_description')
    op.drop_column('campaigns', 'ai_product_name')
