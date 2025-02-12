from django.utils.translation import gettext as _
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from tournament.models import Tournament, TournamentMember
import logging
from user.constants import USER_ID_OVERLORDS
from user.models import User
from chat.models import Message


# This function should be only called by the endpoint lobby/<int:id>/ to add
# the user to the websocket group of the tournament
# For removing the user the following endpoints can be used:
# - touranemnt/delete
# - tournament/leave
#
# Tournament is over
# Also if a user connets to the websocket, the user should be added to the group
# and if the user disconnects, the user should be removed from the group
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def join_tournament_channel(user, tournament_id, activate=True):
    tournament_id_name = f"tournament_{tournament_id}"
    channel_name_user =  cache.get(f'user_channel_{user.id}', None)

    # Check if the user has an active channel
    if not channel_name_user:
        return
    if activate:
        # Add the user to the tournament channel (doesnt matter if the user is already in the channel)
        async_to_sync(channel_layer.group_add)(tournament_id_name, channel_name_user)
    else:
        # Remove the user from the tournament channel
        async_to_sync(channel_layer.group_discard)(tournament_id_name, channel_name_user)

def send_tournament_invites_via_pm(tournament_id):
    from chat.message_utils import create_and_send_overloards_pm

    # Get all users that are invited to the tournament
    tournament_admin = TournamentMember.objects.get(tournament_id=tournament_id, is_admin=True)
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id).exclude(is_admin=True)
    tournament = Tournament.objects.get(id=tournament_id)

    for member in tournament_members:
        # TODO: use the new function: create_overloards_pm()
        create_and_send_overloards_pm(
            tournament_admin.user,
            member.user,
            f"**TI,{tournament_admin.user.id},{member.user.id},#T#{tournament.name}#{tournament.id}#**")

