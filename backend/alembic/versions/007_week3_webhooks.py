"""Week 3: Add inbound events, quotas, and reply tracking

Revision ID: 007_week3_webhooks
Revises: 2bacbfd32c06
Create Date: 2025-12-10 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '007_week3_webhooks'
down_revision = '2bacbfd32c06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if tables/columns exist to make migration idempotent
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Create inbound_events table
    if 'inbound_events' not in inspector.get_table_names():
        op.create_table(
            'inbound_events',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
            sa.Column('provider', sa.String(50), nullable=False),
            sa.Column('event_type', sa.String(50), nullable=False),
            sa.Column('provider_payload', postgresql.JSONB, nullable=False),
            sa.Column('parsed_from', sa.String(255), nullable=True),
            sa.Column('parsed_to', sa.String(255), nullable=True),
            sa.Column('parsed_subject', sa.String(500), nullable=True),
            sa.Column('parsed_body_text', sa.Text, nullable=True),
            sa.Column('parsed_message_id', sa.String(255), nullable=True),
            sa.Column('parsed_in_reply_to', sa.String(255), nullable=True),
            sa.Column('processed', sa.String(20), default='pending', nullable=False),
            sa.Column('processed_at', sa.DateTime, nullable=True),
            sa.Column('processing_error', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        )
        
        # Create indexes for inbound_events
        op.create_index('idx_inbound_events_org_created', 'inbound_events', ['org_id', 'created_at'])
        op.create_index('idx_inbound_events_parsed_to', 'inbound_events', ['parsed_to'])
        op.create_index('idx_inbound_events_event_type', 'inbound_events', ['event_type'])
    else:
        # Table exists, check and create indexes if missing
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('inbound_events')]
        if 'idx_inbound_events_org_created' not in existing_indexes:
            op.create_index('idx_inbound_events_org_created', 'inbound_events', ['org_id', 'created_at'])
        if 'idx_inbound_events_parsed_to' not in existing_indexes:
            op.create_index('idx_inbound_events_parsed_to', 'inbound_events', ['parsed_to'])
        if 'idx_inbound_events_event_type' not in existing_indexes:
            op.create_index('idx_inbound_events_event_type', 'inbound_events', ['event_type'])
    
    # Create org_quotas table
    if 'org_quotas' not in inspector.get_table_names():
        op.create_table(
            'org_quotas',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True, index=True),
            sa.Column('emails_sent_this_period', sa.Integer, default=0, nullable=False),
            sa.Column('period_start', sa.Date, nullable=False, server_default=sa.text('CURRENT_DATE')),
            sa.Column('email_limit_per_period', sa.Integer, default=1000, nullable=False),
            sa.Column('period_type', sa.String(20), default='daily', nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        )
    
    # Create lead_tags table
    if 'lead_tags' not in inspector.get_table_names():
        op.create_table(
            'lead_tags',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('tag', sa.String(100), nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
            sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='CASCADE'),
        )
        
        # Create indexes for lead_tags
        op.create_index('idx_lead_tags_lead_tag', 'lead_tags', ['lead_id', 'tag'], unique=True)
        op.create_index('idx_lead_tags_tag', 'lead_tags', ['tag'])
    
    # Add reply tracking columns to campaign_leads (check if not exists)
    campaign_leads_columns = [col['name'] for col in inspector.get_columns('campaign_leads')]
    if 'replied_at' not in campaign_leads_columns:
        op.add_column('campaign_leads', sa.Column('replied_at', sa.DateTime, nullable=True))
    if 'reply_message_id' not in campaign_leads_columns:
        op.add_column('campaign_leads', sa.Column('reply_message_id', sa.String(255), nullable=True))
    if 'stop_reason' not in campaign_leads_columns:
        op.add_column('campaign_leads', sa.Column('stop_reason', sa.String(100), nullable=True))
    
    # Add bounce tracking to leads (check if not exists)
    leads_columns = [col['name'] for col in inspector.get_columns('leads')]
    if 'do_not_contact' not in leads_columns:
        op.add_column('leads', sa.Column('do_not_contact', sa.Boolean, default=False, nullable=False, server_default='false'))
    if 'bounce_reason' not in leads_columns:
        op.add_column('leads', sa.Column('bounce_reason', sa.String(255), nullable=True))
    if 'bounced_at' not in leads_columns:
        op.add_column('leads', sa.Column('bounced_at', sa.DateTime, nullable=True))
    
    # Create index if not exists
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('leads')]
    if 'idx_leads_do_not_contact' not in existing_indexes:
        op.create_index('idx_leads_do_not_contact', 'leads', ['do_not_contact'])
    
    # Add stop_on_reply to sequence_steps (check if not exists)
    sequence_steps_columns = [col['name'] for col in inspector.get_columns('sequence_steps')]
    if 'stop_on_reply' not in sequence_steps_columns:
        op.add_column('sequence_steps', sa.Column('stop_on_reply', sa.Boolean, default=True, nullable=False, server_default='true'))


def downgrade() -> None:
    # Remove indexes
    try:
        op.drop_index('idx_leads_do_not_contact', table_name='leads')
    except:
        pass
    try:
        op.drop_index('idx_lead_tags_tag', table_name='lead_tags')
    except:
        pass
    try:
        op.drop_index('idx_lead_tags_lead_tag', table_name='lead_tags')
    except:
        pass
    try:
        op.drop_index('idx_inbound_events_event_type', table_name='inbound_events')
    except:
        pass
    try:
        op.drop_index('idx_inbound_events_parsed_to', table_name='inbound_events')
    except:
        pass
    try:
        op.drop_index('idx_inbound_events_org_created', table_name='inbound_events')
    except:
        pass
    
    # Drop columns
    try:
        op.drop_column('sequence_steps', 'stop_on_reply')
    except:
        pass
    try:
        op.drop_column('leads', 'bounced_at')
    except:
        pass
    try:
        op.drop_column('leads', 'bounce_reason')
    except:
        pass
    try:
        op.drop_column('leads', 'do_not_contact')
    except:
        pass
    try:
        op.drop_column('campaign_leads', 'stop_reason')
    except:
        pass
    try:
        op.drop_column('campaign_leads', 'reply_message_id')
    except:
        pass
    try:
        op.drop_column('campaign_leads', 'replied_at')
    except:
        pass
    
    # Drop tables
    try:
        op.drop_table('lead_tags')
    except:
        pass
    try:
        op.drop_table('org_quotas')
    except:
        pass
    try:
        op.drop_table('inbound_events')
    except:
        pass
