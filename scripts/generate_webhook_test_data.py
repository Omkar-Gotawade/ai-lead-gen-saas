"""
Quick script to populate webhook page with test data
Run this to see events in your webhook page
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import uuid

# Database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/leadgen_db"

# Create engine
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Sample data
EMAIL_EVENTS = [
    {
        'event_type': 'delivered',
        'from_emails': ['you@example.com', 'sales@yourcompany.com'],
        'to_emails': ['john@acme.com', 'sarah@techcorp.com', 'mike@startup.io'],
        'subjects': ['Quick question about your SDR team', 'Following up on my previous email', 'Saw your recent LinkedIn post'],
    },
    {
        'event_type': 'bounce',
        'from_emails': ['you@example.com'],
        'to_emails': ['invalid@nonexistent.com', 'old@abandoned.co', 'wrong@typo.com'],
        'subjects': ['Meeting request', 'Quick chat?', 'Demo invitation'],
    },
    {
        'event_type': 'spam',
        'from_emails': ['you@example.com'],
        'to_emails': ['angry@company.com', 'unsubscribe@business.net'],
        'subjects': ['Amazing offer!', 'Last chance', 'Limited time deal'],
    },
    {
        'event_type': 'open',
        'from_emails': ['you@example.com'],
        'to_emails': ['interested@buyer.com', 'curious@enterprise.com', 'engaged@saas.co'],
        'subjects': ['Quick question', 'Thought you might find this interesting', 'Following up'],
    },
    {
        'event_type': 'reply',
        'from_emails': ['john@acme.com', 'sarah@techcorp.com'],  # These are FROM emails (replies FROM leads)
        'to_emails': ['you@example.com', 'sales@yourcompany.com'],  # These are TO emails (replies TO you)
        'subjects': ['Re: Quick question about your SDR team', 'Re: Following up', 'Re: Saw your recent LinkedIn post'],
    },
]

def generate_test_events(count_per_type=5):
    """Generate test webhook events"""
    
    print(f"🔄 Generating {count_per_type} events per type...")
    created = 0
    
    for event_config in EMAIL_EVENTS:
        event_type = event_config['event_type']
        
        for i in range(count_per_type):
            try:
                # Random time in last 7 days
                hours_ago = random.randint(0, 7 * 24)
                created_at = datetime.utcnow() - timedelta(hours=hours_ago)
                
                # Random emails
                from_email = random.choice(event_config['from_emails'])
                to_email = random.choice(event_config['to_emails'])
                subject = random.choice(event_config['subjects'])
                
                # Build raw payload
                raw_payload = {
                    'event': event_type,
                    'email': to_email if event_type != 'reply' else from_email,
                    'timestamp': int(created_at.timestamp()),
                    'sg_event_id': f"{event_type}-{uuid.uuid4().hex[:8]}",
                }
                
                if event_type == 'bounce':
                    raw_payload['reason'] = random.choice([
                        '550 5.1.1 User unknown',
                        '550 5.7.1 Blocked',
                        '552 5.2.2 Mailbox full'
                    ])
                    raw_payload['type'] = 'bounce'
                
                if event_type == 'reply':
                    raw_payload['body'] = random.choice([
                        'Thanks for reaching out! Let me check with my team.',
                        'This sounds interesting. Can we schedule a call?',
                        'Not interested right now, but thanks.',
                        'Please send more information.',
                        'Let me loop in our VP of Sales.'
                    ])
                
                # Insert into database
                insert_query = text("""
                INSERT INTO inbound_events 
                (event_type, provider, parsed_from, parsed_to, parsed_subject, raw_payload, created_at)
                VALUES 
                (:event_type, :provider, :parsed_from, :parsed_to, :parsed_subject, :raw_payload, :created_at)
                """)
                
                session.execute(insert_query, {
                    'event_type': event_type,
                    'provider': 'sendgrid',
                    'parsed_from': from_email,
                    'parsed_to': to_email,
                    'parsed_subject': subject,
                    'raw_payload': str(raw_payload),
                    'created_at': created_at
                })
                
                created += 1
                print(f"  ✅ {event_type.upper()}: {from_email} → {to_email}")
                
            except Exception as e:
                print(f"  ❌ Error creating {event_type} event: {e}")
                session.rollback()
    
    try:
        session.commit()
        print(f"\n🎉 Successfully created {created} webhook events!")
        print(f"🌐 View them at: http://localhost:5173/webhooks")
    except Exception as e:
        print(f"\n❌ Error committing events: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  WEBHOOK TEST DATA GENERATOR")
    print("=" * 60)
    print()
    
    # Check if events already exist
    result = session.execute(text("SELECT COUNT(*) FROM inbound_events"))
    existing_count = result.fetchone()[0]
    
    if existing_count > 0:
        print(f"⚠️  Warning: {existing_count} events already exist in database")
        response = input("Continue and add more? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    generate_test_events(count_per_type=5)
    
    print()
    print("=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)
    print("1. Open http://localhost:5173/webhooks in your browser")
    print("2. Click the filter buttons: Delivered, Replies, Bounces, etc.")
    print("3. You should see the test events!")
    print()
    print("To clear test data:")
    print('  docker exec -it leadgen_postgres psql -U postgres -d leadgen_db -c "DELETE FROM inbound_events;"')
    print("=" * 60)
