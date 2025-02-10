import logging
from django.core.cache import cache
from tournament.models import TournamentMember
from chat.models import ConversationMember
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from .constants import PRE_USER_CHANNEL, PRE_CONVERSATION, PRE_TOURNAMENT
channel_layer = get_channel_layer()

# GROUP PRE SHOULD BE PRE_CONVERSATION, PRE_TOURNAMENT or PRE_GAME (TODO: implement PRE_GAME use)
# This is the only function which should use 'channel_layer.group_...'
async def update_client_in_group(user_id, object_id, group_pre, add = True):
    group_name = f"{group_pre}{object_id}"
    channel_name_user = await sync_to_async(cache.get)(f"{PRE_USER_CHANNEL}{user_id}")
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
    logging.info("now")
    conversation_memberships = list(ConversationMember.objects.filter(user=user))
    logging.info(f"Adding/removing user ({user}) to all their conversation groups. Adding: {add}. Total: {len(conversation_memberships)}")
    logging.info("then")
    for membership in conversation_memberships:
        logging.info("loop")
        async_to_sync(update_client_in_group)(user.id, membership.conversation.id, PRE_CONVERSATION, add)

@sync_to_async
def update_client_in_all_tournament_groups(user, add = True):
    # Get all tournament IDs where the user is a member and state is not 'finished'
    tournament_memberships = list(TournamentMember.objects.filter(user=user, tournament__state__in=['setup', 'ongoing']))
    logging.info(f"Adding/removing user ({user}) to all their tournament groups. Adding: {add}. Total: {len(tournament_memberships)}")
    for membership in tournament_memberships:
        async_to_sync(update_client_in_group)(user.id, membership.conversation.id, PRE_TOURNAMENT, add)