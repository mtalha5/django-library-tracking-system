import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')

app = Celery('library_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
CELERY_BEAT_SCHEDULE={
    "check-over-due-loans":{
        "task":"library.tasks.check_over_due_loans",
        "schedule": crontab(hour=8,minute=0)
    }
}