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
# Tournament is over
# Also if a user connets to the websocket, the user should be added to the group
# and if the user disconnects, the user should be removed from the group
def join_tournament_channel(user, tournament_id, activate=True):
    tournament_id_name = f"tournament{tournament_id}"
    channel_name_user =  cache.get(f'user_channel_{user.id}', None)

    if channel_name_user:
        # Check if the user is already in the tournament channel
        user_in_channel = cache.get(f"user_in_channel_{user.id}_{tournament_id_name}", False)
        if activate:
            if not user_in_channel:
                # Add the user to the tournament channel
                async_to_sync(channel_layer.group_add)(tournament_id_name, channel_name_user)
                # Update the record to indicate the user is now in the channel
                cache.set(f"user_in_channel_{user.id}_{tournament_id_name}", True)
                async_to_sync(channel_layer.group_send)(
                tournament_id_name,
                {
                    "messageType": "tournamentSubscription",
                    "type": "tournament_subscription",
                    "tournamentId": tournament_id,
                    "userId":user.id,
                    "state": "viewing"
                })
                logging.info(f"User {user} added to tournament {tournament_id} channel")
            else:
                logging.info(f"User {user} is already in tournament {tournament_id} channel")
        else:
            if user_in_channel:
                # Remove the user from the tournament channel
                async_to_sync(channel_layer.group_discard)(tournament_id_name, channel_name_user)
                # Update the record to indicate the user is no longer in the channel
                cache.set(f"user_in_channel_{user.id}_{tournament_id_name}", False)
                async_to_sync(channel_layer.group_send)(
                tournament_id_name,
                {
                    "messageType": "tournamentSubscription",
                    "type": "tournament_subscription",
                    "tournamentId": tournament_id,
                    "userId":user.id,
                    "state": "notViewing"
                })
                logging.info(f"User {user} removed from tournament {tournament_id} channel")
            else:
                logging.info(f"User {user} is not in tournament {tournament_id} channel")
    else:
        logging.warning(f"User {user} does not have an active channel")
    logging.info(f"User {user} joined tournament {tournament_id} - websocket message was sent")


def send_tournament_ws_msg(tournament_id, type_camel, type_snake, message, **json_details):
    tournament_id_name = f"tournament{tournament_id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": type_camel,
        "type": type_snake,
        "tournamentId": tournament_id,
        "message": message,
        **json_details
    })
    logging.info(f"Message sent to tournament {tournament_id} channel")