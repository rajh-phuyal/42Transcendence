from django.utils.translation import gettext as _
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from tournament.models import Tournament, TournamentMember
from services.websocket_utils import send_message_to_user_sync
import logging
from .serializer import TournamentMemberSerializer
from user.constants import USER_ID_OVERLOARDS
from user.models import User
from chat.models import Message
from services.chat_service import broadcast_message


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
    logging.info(f"Message sent to tournament {tournament_id} channel: {message}")

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

    # Check if the user has an active channel
    if not channel_name_user:
        return
    if activate:
        # Add the user to the tournament channel (doesnt matter if the user is already in the channel)
        async_to_sync(channel_layer.group_add)(tournament_id_name, channel_name_user)
        data = TournamentMemberSerializer(TournamentMember.objects.get(user_id=user.id, tournament_id=tournament_id)).data
        # TODO Implelemnt the tournament state
        send_tournament_ws_msg(
            tournament_id,
            "tournamentFan",
            "tournament_fan",
            _("User {username} is watching the tournament page").format(username=user.username),
            **{"state": "True"}
        )
    else:
        # Remove the user from the tournament channel
        async_to_sync(channel_layer.group_discard)(tournament_id_name, channel_name_user)
        send_tournament_ws_msg(
            tournament_id,
            "tournamentFan",
            "tournament_fan",
            _("User {username} is not watching the tournament page anymore").format(username=user.username),
            **{"state": "False"}
        )

def send_tournament_invites_via_pm(tournament_id):
    from chat.utils import create_conversation, get_conversation
    # Get all users that are invited to the tournament
    tournament_admin = TournamentMember.objects.get(tournament_id=tournament_id, is_admin=True)
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id).exclude(is_admin=True)
    tournament = Tournament.objects.get(id=tournament_id)

    for member in tournament_members:
        # Check if there's a private conversation between the user and the admin
        conversation = get_conversation(tournament_admin, member)
        invite_message = _("The overloads spectace that the holly {username} has invited you to the fantastic tournament {tournament_name}").format(username=tournament_admin.user.username, tournament_name=tournament.name)
        
        # If not, create one
        if not conversation:
            conversation = create_conversation(tournament_admin, member, invite_message)
            continue
        
        # Create overloards message in the DB
        overlords = User.objects.get(id=USER_ID_OVERLOARDS) 
        newMessage = Message.objects.create(user=overlords, conversation=conversation, content=invite_message)
        newMessage.save()

        # Send a message to an existing conversation
        broadcast_message(newMessage)




def send_tournament_invites_via_ws(tournament_id):
    # Get all users that are invited to the tournament
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id).exclude(is_admin=True)

    #TODO: Since we don't have the notification system implemented yet, and no
    # private chat with the overloards, we can't send a persitent message to the
    # yet. But anyhow we can send a toat message to the user (done below)
    # and the user can see the invite in the modal done by issue #234

    # Also send an info message that will show as a toast message
    message={
        "messageType": "info",
        "type": "info",
        "message": _("You have been invited to a tournament check it out in the join tournament modal"),
    }
    for member in tournament_members:
        send_message_to_user_sync(member.user_id, **message)


def delete_tournament_channel(tournament_id):
    # Remove all users from the tournament channel
    tournament_id_name = f"tournament{tournament_id}"
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id)
    for member in tournament_members:
        channel_name_user =  cache.get(f'user_channel_{member.user.id}', None)
        if not channel_name_user:
            continue
        async_to_sync(channel_layer.group_discard)(tournament_id_name, channel_name_user)
        logging.info(f"Removed user {member.user.username} from tournament {tournament_id} channel")
    logging.info(f"Removed all users from tournament {tournament_id} channel")
    # Remove the tournament channel
    # This in not needed since the channel will be removed automatically by
    # the channel layer