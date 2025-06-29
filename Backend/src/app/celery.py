from __future__ import absolute_import, unicode_literals
import logging
import os
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# All celery-related config keys should have the `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_connection_retry_on_startup = True

# Auto-discover tasks from all installed apps.
app.autodiscover_tasks()

@worker_ready.connect
def startup_update_tournament_deadlines(sender, **kwargs):
    # Do your startup logic here
    from tournament.tasks import startup_check_deadline
    startup_check_deadline.delay()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'check-for-overdue-games': {
        'task': 'tournament.tasks.check_overdue_tournament_games',
        'schedule': timedelta(seconds=5),  # Run every 5 seconds
    },
}