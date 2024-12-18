from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
import logging

# This function should be only called by the endpoint lobby/<int:id>/ to add
# the user to the websocket group of the tournament
# For removing the user the following endpoints can be used:
# - touranemnt/delete
# - tournament/leave
#
# Also if a user connets to the websocket, the user should be added to the group
# and if the user disconnects, the user should be removed from the group
def join_tournament_channel(user, tournament_id, activate=True):
    tournament_id_name = f"tournament{tournament_id}"
    channel_name_user =  cache.get(f'user_channel_{user.id}', None)
    if channel_name_user:
        async_to_sync(channel_layer.group_add)(tournament_id_name, channel_name_user)
    async_to_sync(channel_layer.group_send)(
        tournament_id_name,
        {
            "messageType": "tournamentSubscription",
            "type": "tournament_subscription",
            "userId":user.id,
            "state": "join"
        })
    logging.info(f"User {user} joined tournament {tournament_id} - websocket message was sent")