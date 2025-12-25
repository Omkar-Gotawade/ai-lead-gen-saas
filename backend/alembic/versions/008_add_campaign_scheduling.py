"""add next_run_at and current_step_index to campaign_leads

Revision ID: 008
Revises: 007
Create Date: 2024-12-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007_week3_webhooks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add next_run_at column
    op.add_column('campaign_leads', 
        sa.Column('next_run_at', sa.DateTime(), nullable=True)
    )
    
    # Add current_step_index column
    op.add_column('campaign_leads', 
        sa.Column('current_step_index', sa.Integer(), nullable=False, server_default='0')
    )
    
    # Add last_sent_at if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'campaign_leads' AND column_name = 'last_sent_at'
            ) THEN
                ALTER TABLE campaign_leads ADD COLUMN last_sent_at TIMESTAMP;
            END IF;
        END $$;
    """)
    
    # Update status enum to include 'pending'
    op.execute("UPDATE campaign_leads SET status = 'pending' WHERE status = 'queued'")


def downgrade() -> None:
    op.drop_column('campaign_leads', 'current_step_index')
    op.drop_column('campaign_leads', 'next_run_at')
