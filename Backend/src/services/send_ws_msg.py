# Basics
import logging
# Django
from django.utils import timezone
from django.db.models import Sum
from django.utils.translation import gettext as _
# Asgiref
from asgiref.sync import sync_to_async, async_to_sync
# Channels
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Services
from services.constants import PRE_GROUP_CONVERSATION, PRE_GROUP_GAME, PRE_GROUP_TOURNAMENT
# User
from user.constants import AVATAR_OVERLORDS, USERNAME_OVERLORDS, USER_ID_OVERLORDS
from user.models import User
# Chat
from chat.models import ConversationMember, Conversation
from chat.serializers import MessageSerializer, ConversationsSerializer
# Game
from game.models import Game
from game.game_cache import get_game_data
# Tournament
from tournament.models import Tournament, TournamentMember
from tournament.serializer import TournamentInfoSerializer, TournamentMemberSerializer, TournamentGameSerializer

""" All WS Message should be send to the FE using one of the following functions:"""

# ==============================================================================
#     BASIC FUNCTIONS
# ==============================================================================
async def send_ws_msg_to_user(user, **message):
    """ Basic function to send a message to a user via WebSocket """
    if isinstance(user, int):
        user = await sync_to_async(User.objects.get)(id=user)
    channel_name =  await sync_to_async(user.get_ws_channel_name)()
    if channel_name:
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user}.")

async def send_ws_info_msg(user_id, content):
    message_dict = {
        "messageType": "info",
        "type": "info",
        "message": content
    }
    await send_ws_msg_to_user(user_id, **message_dict)

async def send_ws_error_msg(user_id, content):
    if not user_id or not content:
        return
    message_dict = {
        "messageType": "error",
        "type": "error",
        "message": content
    }
    await send_ws_msg_to_user(user_id, **message_dict)

@sync_to_async
def send_ws_badge(user_id, conversation_id):
    unread_count = ConversationMember.objects.get(user=user_id, conversation=conversation_id).unread_counter
    msg_data = {
        "messageType": "updateBadge",
        "type": "update_badge",
        "what": "conversation",
        "id": conversation_id,
        "value": unread_count
    }
    async_to_sync(send_ws_msg_to_user)(user_id, **msg_data)

@sync_to_async
def send_ws_badge_all(user_id):
    conversation_memberships = ConversationMember.objects.filter(user=user_id)
    chat_unread_counter = conversation_memberships.aggregate(total_unread=Sum('unread_counter'))['total_unread'] or 0
    msg_data = {
        "messageType": "updateBadge",
        "type": "update_badge",
        "what": "all",
        "value": chat_unread_counter
    }
    async_to_sync(send_ws_msg_to_user)(user_id, **msg_data)

# ==============================================================================
#     PROFILE FUNCTIONS
# ==============================================================================
def send_ws_update_relationship(user_changed, user_viewer):
    """
    This function is send if user_changed changes his relationship status to
    user_viewer. If the user_viewer is online, he will receive this message. The
    fe checks it user_viewer is watching the profile of the user_changed and
    only then reloads the profile view.
    """
    message_dict = {
        "messageType": "reloadProfile",
        "type": "reload_profile",
        "message": _("Relationship status has changed."),
        "userId": user_changed.id
    }
    async_to_sync(send_ws_msg_to_user)(user_viewer, **message_dict)
# ==============================================================================
#     CHAT FUNCTIONS
# ==============================================================================
class TempConversationMessage:
    def __init__(self, overlords_instance, conversation, created_at, content):
        self.id = None
        self.conversation = conversation
        self.user = overlords_instance
        self.username = USERNAME_OVERLORDS
        self.avatar_path = AVATAR_OVERLORDS
        self.created_at = created_at
        self.seen_at = None
        self.content = content

async def send_ws_chat(message_object):
    serialized_message = await sync_to_async(lambda: MessageSerializer(instance=message_object).data)()
    # Send to conversation channel
    group_name = f"{PRE_GROUP_CONVERSATION}{message_object.conversation.id}"
    await channel_layer.group_send(group_name, serialized_message)

async def send_ws_chat_temporary(user_id, conversation_id, content):
    overloards = await sync_to_async(User.objects.get)(id=USER_ID_OVERLORDS)
    try:
        conversation = await sync_to_async(Conversation.objects.get)(id=conversation_id)
    except Conversation.DoesNotExist:
        logging.error(f"Conversation with ID {conversation_id} not found.")
        return
    message = TempConversationMessage(overlords_instance=overloards, conversation=conversation, created_at=timezone.now().isoformat(), content=content) # TODO: Issue #193
    serialized_message = await sync_to_async(lambda: MessageSerializer(instance=message).data)()
    await send_ws_msg_to_user(user_id, **serialized_message)

async def send_ws_new_conversation(user, conversation):
    """
    Sends a special WS Message so in case the user has chat opened, the frontend
    can create a new conversation card.
    Function allows user and conversation to be instances or IDs.
    """
    if isinstance(user, int):
        user = await sync_to_async(User.objects.get)(id=user)
    if isinstance(conversation, int):
        conversation = await sync_to_async(Conversation.objects.get)(id=conversation)
    serialized_conversation = await sync_to_async(lambda: ConversationsSerializer(instance=conversation, context={'user': user}).data)()
    # Add the messageType and type
    serialized_conversation['messageType'] = "newConversation"
    serialized_conversation['type'] = "new_conversation"
    await send_ws_msg_to_user(user, **serialized_conversation)

# ==============================================================================
#     TOURNAMENT FUNCTIONS
# ==============================================================================
def send_ws_tournament_info_msg(tournament, deleted=False):
    """
    Since a deleted tournament is not in the db anymore we need to call this
    function right before we delete the entry. In this case we set the deleted
    flag to True.
    """
    if isinstance(tournament, int):
        tournament = Tournament.objects.get(id=tournament)

    serializerInfo = TournamentInfoSerializer(tournament)
    if deleted:
        # Since the return is read only we need to make a copy to change the state
        info_data = serializerInfo.data.copy()
        info_data['state'] = "deleted"
    else:
        info_data = serializerInfo.data
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{tournament.id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": "tournamentInfo",
        "type": "tournament_info",
        "tournamentInfo": info_data
    })

def send_ws_tournament_member_msg(tournament_member, leave=False):
    """
    Since a player who has left a tournament is not in the db table
    tournament_member anymore we need to call this function right before we
    delete the entry. In this case we set the leave flag to True.
    """
    if isinstance(tournament_member, int):
        tournament_member = TournamentMember.objects.get(id=tournament_member)

    serializer_member = TournamentMemberSerializer(tournament_member)
    if leave:
        # Since the return is read only we need to make a copy
        member_data = serializer_member.data.copy()
        member_data['state'] = "left"
    else:
        member_data = serializer_member.data
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{tournament_member.tournament.id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": "tournamentMember",
        "type": "tournament_member",
        "tournamentMember": member_data
    })

def send_ws_all_tournament_members_msg(tournament):
    """
    This function sends all tournament members to the group of the tournament.
    As a sorted list
    """
    if isinstance(tournament, int):
        tournament = Tournament.objects.get(id=tournament)
    members = TournamentMember.objects.filter(tournament=tournament).order_by('rank')
    serializer_members = TournamentMemberSerializer(members, many=True)
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{tournament.id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": "tournamentMembers",
        "type": "tournament_members",
        "tournamentMembers": serializer_members.data
    })

def send_ws_tournament_game_msg(game):
    if isinstance(game, int):
        game = Game.objects.get(id=game)
    if game.tournament_id is None:
        return
    serializerGame = TournamentGameSerializer(game)
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{game.tournament.id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": "tournamentGame",
        "type": "tournament_game",
        "TournamentGame": serializerGame.data
    })

def send_ws_tournament_pm(tournament_id, message):
    """
    This function sends a PM Chat Message to all users in a tournament.
    if the message contains <userid> it will be replaced with the actual user id.
    """
    from tournament.models import TournamentMember, Tournament
    from chat.message_utils import create_and_send_overloards_pm
     # Get all users that are invited to the tournament
    tournament_admin = TournamentMember.objects.get(tournament_id=tournament_id, is_admin=True)
    tournament_members = TournamentMember.objects.filter(tournament_id=tournament_id).exclude(is_admin=True)

    for member in tournament_members:
        #if message contains <userid> replace it with the actual user id
        temp = message
        if "<userid>" in temp:
            temp = temp.replace("<userid>", str(member.user.id))
        create_and_send_overloards_pm(tournament_admin.user, member.user, temp)

# ==============================================================================
#     GAME FUNCTIONS
# ==============================================================================
async def send_ws_game_players_ready_msg(game_id, left_ready, right_ready, start_time = None):
    group_name = f"{PRE_GROUP_GAME}{game_id}"
    await channel_layer.group_send(
        group_name,
        {
            "type": "update_players_ready",
            "messageType": "playersReady",
            "playerLeft": left_ready,
            "playerRight": right_ready,
            "startTime": start_time
        }
    )

async def send_ws_game_data_msg(game_id):
    game_state_data = get_game_data(game_id)
    if not game_state_data:
        logging.error(f"Game state not found for game {game_id} so it can't be send as a ws message!")
        return
    group_name = f"{PRE_GROUP_GAME}{game_id}"
    await channel_layer.group_send(
        group_name,
        {
            "type": "update_game_state",
            "messageType": "gameState",
            **game_state_data
        }
    )

async def send_ws_game_finished(game_id):
    group_name = f"{PRE_GROUP_GAME}{game_id}"
    await channel_layer.group_send(group_name, {"type": "game_finished"})