from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from tournament.models import TournamentMember
import logging
User = get_user_model()
channel_layer = get_channel_layer()

# channel_name is the WebSocket connection ID for a user
# group_name is the conversation ID
@sync_to_async
def setup_all_tournament_channels(user, channel_name, intialize=True):
    logging.info("MODE: %d, Configuring tournaments channels for user: %s with channel_name: %s", intialize, user, channel_name)
    # Get all tournament IDs where the user is a member and state is not 'finished'
    tournament_memberships = TournamentMember.objects.filter(user=user, tournament__state__in=['setup', 'ongoing'])
    for membership in tournament_memberships:
        group_name = f"tournament_{membership.tournament.id}"
        if intialize:
            async_to_sync(channel_layer.group_add)(group_name, channel_name)
            logging.info(f"\tAdded user {user} to group {group_name}")
        else:
            async_to_sync(channel_layer.group_discard)(group_name, channel_name)
            logging.info(f"\tRemoved user {user} from group {group_name}")