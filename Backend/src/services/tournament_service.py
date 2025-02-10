from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from tournament.models import TournamentMember
import logging
User = get_user_model()
channel_layer = get_channel_layer()




