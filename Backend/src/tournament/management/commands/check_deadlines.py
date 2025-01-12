from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

#TODO: HACKATHON:Check if this is needed!
class Command(BaseCommand):
    help = 'Check game deadlines and trigger actions'

    def handle(self, *args, **options):
        now = timezone.now()
        #overdue_games = Game.objects.filter(deadline__lte=now, status='pending')
        logging.info(f"Checking game deadlines at {now}")
