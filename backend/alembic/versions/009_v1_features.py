"""add_v1_features_lead_discovery_linkedin_warmup

Revision ID: 009_v1_features
Revises: 008_add_campaign_scheduling
Create Date: 2025-12-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '009_v1_features'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """Apply v1 features: Lead Discovery, LinkedIn Enrichment, Email Warmup."""
    
    # 1. Create lead_discovery_jobs table
    op.create_table(
        'lead_discovery_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('org_id', UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('keywords', sa.String(500), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('industry', sa.String(200), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, index=True, server_default='pending'),
        sa.Column('domains_found', sa.Integer, nullable=True, server_default='0'),
        sa.Column('domains_crawled', sa.Integer, nullable=True, server_default='0'),
        sa.Column('leads_created', sa.Integer, nullable=True, server_default='0'),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )
    
    # 2. Create discovered_domains table
    op.create_table(
        'discovered_domains',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('discovery_job_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('domain', sa.String(500), nullable=False, index=True),
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, index=True, server_default='pending'),
        sa.Column('company_name', sa.String(500), nullable=True),
        sa.Column('company_description', sa.Text, nullable=True),
        sa.Column('emails_found', sa.Text, nullable=True),
        sa.Column('raw_content', sa.Text, nullable=True),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('crawled_at', sa.DateTime, nullable=True),
        sa.ForeignKeyConstraint(['discovery_job_id'], ['lead_discovery_jobs.id'], ondelete='CASCADE'),
    )
    
    # 3. Add LinkedIn fields to leads table
    op.add_column('leads', sa.Column('linkedin_url', sa.String(500), nullable=True))
    op.add_column('leads', sa.Column('job_title', sa.String(255), nullable=True))
    op.add_column('leads', sa.Column('seniority', sa.String(100), nullable=True))
    op.add_column('leads', sa.Column('company_size', sa.String(100), nullable=True))
    op.add_column('leads', sa.Column('linkedin_headline', sa.String(500), nullable=True))
    
    # 4. Create email_warmup_domains table
    op.create_table(
        'email_warmup_domains',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('org_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('domain', sa.String(500), nullable=False, index=True),
        sa.Column('daily_limit', sa.Integer, nullable=False, server_default='10'),
        sa.Column('warmup_day', sa.Integer, nullable=False, server_default='1'),
        sa.Column('emails_sent_today', sa.Integer, nullable=False, server_default='0'),
        sa.Column('last_reset_date', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )


def downgrade():
    """Rollback v1 features."""
    
    # Drop tables
    op.drop_table('email_warmup_domains')
    op.drop_table('discovered_domains')
    op.drop_table('lead_discovery_jobs')
    
    # Remove LinkedIn columns from leads
    op.drop_column('leads', 'linkedin_headline')
    op.drop_column('leads', 'company_size')
    op.drop_column('leads', 'seniority')
    op.drop_column('leads', 'job_title')
    op.drop_column('leads', 'linkedin_url')
