-- Insert test webhook events for demonstration
-- First, get the user's org_id (assuming first user)
DO $$
DECLARE
  user_org_id UUID;
BEGIN
  SELECT id INTO user_org_id FROM users LIMIT 1;
  
  -- If no user exists, create a default org_id
  IF user_org_id IS NULL THEN
    user_org_id := gen_random_uuid();
  END IF;

  -- Insert test webhook events
  INSERT INTO inbound_events (id, org_id, event_type, provider, provider_payload, parsed_from, parsed_to, parsed_subject, created_at)
  VALUES 
    -- Delivered events (3)
    (gen_random_uuid(), user_org_id, 'delivered', 'sendgrid', '{}', 'you@example.com', 'john@acme.com', 'Quick question about your SDR team', NOW() - INTERVAL '2 hours'),
    (gen_random_uuid(), user_org_id, 'delivered', 'sendgrid', '{}', 'you@example.com', 'sarah@techcorp.com', 'Following up on my email', NOW() - INTERVAL '4 hours'),
    (gen_random_uuid(), user_org_id, 'delivered', 'sendgrid', '{}', 'you@example.com', 'mike@startup.io', 'Saw your LinkedIn post', NOW() - INTERVAL '6 hours'),
    
    -- Bounce events (2)
    (gen_random_uuid(), user_org_id, 'bounce', 'sendgrid', '{"reason":"550 User unknown"}', 'you@example.com', 'invalid@nonexistent.com', 'Meeting request', NOW() - INTERVAL '8 hours'),
    (gen_random_uuid(), user_org_id, 'bounce', 'sendgrid', '{"reason":"552 Mailbox full"}', 'you@example.com', 'old@abandoned.co', 'Quick chat?', NOW() - INTERVAL '12 hours'),
    
    -- Spam reports (1)
    (gen_random_uuid(), user_org_id, 'spam', 'sendgrid', '{}', 'you@example.com', 'angry@company.com', 'Limited time offer', NOW() - INTERVAL '10 hours'),
    
    -- Open events (3)
    (gen_random_uuid(), user_org_id, 'open', 'sendgrid', '{}', 'you@example.com', 'interested@buyer.com', 'Quick question', NOW() - INTERVAL '1 hour'),
    (gen_random_uuid(), user_org_id, 'open', 'sendgrid', '{}', 'you@example.com', 'john@acme.com', 'Quick question about your SDR team', NOW() - INTERVAL '90 minutes'),
    (gen_random_uuid(), user_org_id, 'open', 'sendgrid', '{}', 'you@example.com', 'engaged@saas.co', 'Thought you might find this interesting', NOW() - INTERVAL '3 hours'),
    
    -- Reply events (2)
    (gen_random_uuid(), user_org_id, 'reply', 'gmail', '{"body":"Thanks for reaching out! Let me check with my team."}', 'john@acme.com', 'you@example.com', 'Re: Quick question about your SDR team', NOW() - INTERVAL '30 minutes'),
    (gen_random_uuid(), user_org_id, 'reply', 'gmail', '{"body":"This sounds interesting. Can we schedule a call?"}', 'sarah@techcorp.com', 'you@example.com', 'Re: Following up on my email', NOW() - INTERVAL '45 minutes');
    
END $$;
