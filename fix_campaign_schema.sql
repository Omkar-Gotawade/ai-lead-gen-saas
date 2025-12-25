-- Add missing columns to campaign_leads table
ALTER TABLE campaign_leads ADD COLUMN IF NOT EXISTS next_run_at TIMESTAMP;
ALTER TABLE campaign_leads ADD COLUMN IF NOT EXISTS current_step_index INTEGER DEFAULT 0;
ALTER TABLE campaign_leads ADD COLUMN IF NOT EXISTS last_sent_at TIMESTAMP;

-- Update status from 'queued' to 'pending'
UPDATE campaign_leads SET status = 'pending' WHERE status = 'queued';

-- Set next_run_at to now for all pending leads
UPDATE campaign_leads SET next_run_at = NOW() WHERE status = 'pending';

SELECT 'Migration completed!' as result;
