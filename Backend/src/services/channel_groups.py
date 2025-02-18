import logging
from django.core.cache import cache
from tournament.models import TournamentMember
from chat.models import ConversationMember
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from .constants import PRE_CHANNEL_USER, PRE_GROUP_CONVERSATION, PRE_GROUP_TOURNAMENT
channel_layer = get_channel_layer()
from user.models import User

async def update_client_in_group(user, object_id, group_pre, add = True):
    """
    This function should be the only one using group_add and group_discard
    It will add/remove a user to/from a group
    """
    if isinstance(user, int):
        user = await sync_to_async(User.objects.get)(id=user)

    channel_name_user = await sync_to_async(user.get_ws_channel_name)()
    group_name = f"{group_pre}{object_id}"
    if not channel_name_user:
        # User is not online
        return
    if add:
        await channel_layer.group_add(group_name, channel_name_user)
    else:
        await channel_layer.group_discard(group_name, channel_name_user)

@sync_to_async
def update_client_in_all_conversation_groups(user, add = True):
    # Get all conversation IDs where the user is a member
    conversation_memberships = list(ConversationMember.objects.filter(user=user))
    logging.info(f"Adding/removing user ({user}) to all their conversation groups. Adding: {add}. Total: {len(conversation_memberships)}")
    for membership in conversation_memberships:
        async_to_sync(update_client_in_group)(user, membership.conversation.id, PRE_GROUP_CONVERSATION, add)

@sync_to_async
def update_client_in_all_tournament_groups(user, add = True):
    # Get all tournament IDs where the user is a member and state is not 'finished'
    tournament_memberships = list(TournamentMember.objects.filter(user=user, tournament__state__in=['setup', 'ongoing']))
    logging.info(f"Adding/removing user ({user}) to all their tournament groups. Adding: {add}. Total: {len(tournament_memberships)}")
    for membership in tournament_memberships:
        async_to_sync(update_client_in_group)(user, membership.tournament.id, PRE_GROUP_TOURNAMENT, add)

def delete_tournament_group(tournament_id):
    # Remove all users from the tournament channel
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{tournament_id}"
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id)
    for member in tournament_members:
        update_client_in_group(member.user, tournament_id, PRE_GROUP_TOURNAMENT, False)
    logging.info(f"Removed all users from tournament {tournament_id} channel ({tournament_id_name})")
    # Remove the tournament channel itself is not needed since the channel
    # will be removed automatically by the channel layer