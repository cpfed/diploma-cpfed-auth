import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpfed.settings")


app = Celery('cpfed')

app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/1',
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    task_track_started=True,
)

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'schedule-contest-notifications': {
        'task': 'telegram_bot.tasks.schedule_contest_notifications',
        'schedule': crontab(hour="0", minute="0"),  # Run at midnight every day
    },
}