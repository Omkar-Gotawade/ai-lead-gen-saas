"""Check email sending status"""
import sys
sys.path.insert(0, 'd:/lead gen/backend')

from app.database import SessionLocal
from app.models.sending_log import SendingLog

db = SessionLocal()

print("="*60)
print("EMAIL SENDING LOGS (Last 10)")
print("="*60)

logs = db.query(SendingLog).order_by(SendingLog.created_at.desc()).limit(10).all()

if not logs:
    print("No email logs found")
else:
    for log in logs:
        print(f"\nTime: {log.created_at}")
        print(f"To: {log.to_email}")
        print(f"Subject: {log.subject}")
        print(f"Status: {log.status.value}")
        print(f"Error: {log.error_message or 'None'}")
        print("-"*60)

db.close()
