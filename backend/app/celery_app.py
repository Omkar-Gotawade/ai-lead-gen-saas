"""Celery worker configuration."""
from celery import Celery
from celery.schedules import crontab
from .config import settings

# Create Celery app
celery_app = Celery(
    "leadgen_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks",
        "app.workers.email_worker",
        "app.workers.campaign_worker",
        "app.workers.lead_discovery_worker"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Celery Beat schedule - check for campaign tasks every minute
celery_app.conf.beat_schedule = {
    'check-campaign-tasks': {
        'task': 'check_pending_campaigns',
        'schedule': 60.0,  # Run every 60 seconds
    },
}
