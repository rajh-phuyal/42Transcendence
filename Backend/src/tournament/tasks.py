from celery import shared_task
from django.utils import timezone
import logging

@shared_task(ignore_result=True)
def hello_world():
    now = timezone.now()
    logging.info("Running it now: %s" % now)
