"""add campaign_leads table

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'campaign_leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('last_step_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for faster lookups
    op.create_index('ix_campaign_leads_campaign_id', 'campaign_leads', ['campaign_id'])
    op.create_index('ix_campaign_leads_lead_id', 'campaign_leads', ['lead_id'])
    op.create_index('ix_campaign_leads_status', 'campaign_leads', ['status'])


def downgrade() -> None:
    op.drop_index('ix_campaign_leads_status', table_name='campaign_leads')
    op.drop_index('ix_campaign_leads_lead_id', table_name='campaign_leads')
    op.drop_index('ix_campaign_leads_campaign_id', table_name='campaign_leads')
    op.drop_table('campaign_leads')
