from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from user.constants import AVATAR_OVERLORDS, USERNAME_OVERLORDS, USER_ID_OVERLORDS
from services.constants import PRE_GROUP_CONVERSATION
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone
from chat.serializers import MessageSerializer
from game.game_cache import get_game_data
from django.core.cache import cache
from django.db.models import Sum
from services.constants import PRE_CHANNEL_USER, PRE_GROUP_GAME, PRE_GROUP_TOURNAMENT
import logging, json
from chat.models import ConversationMember, Message, Conversation
from asgiref.sync import async_to_sync
from user.models import User
# TODO: REMOVE WHEN FINISHED #284

""" All WS Message should be send to the FE using one of the following functions:"""

# ==============================================================================
#     BASIC FUNCTIONS
# ==============================================================================
async def send_ws_msg_to_user(user_id, **message):
    """ Basic function to send a message to a user via WebSocket """
    channel_name =  cache.get(f'{PRE_CHANNEL_USER}{user_id}')
    if channel_name:
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user_id}.")

async def send_ws_info_msg(user_id, content):
    message_dict = {
        "messageType": "info",
        "type": "info",
        "message": content
    }
    await send_ws_msg_to_user(user_id, **message_dict)

async def send_ws_error_msg(user_id, content):
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
    logging.info(f"created temp message: {message}")
    serialized_message = await sync_to_async(lambda: MessageSerializer(instance=message).data)()
    logging.info(f"serialized temp message: {serialized_message}")
    await send_ws_msg_to_user(user_id, **serialized_message)
    logging.info(f"sent temp message: {serialized_message}")

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
    serialized_conversation = await sync_to_async(lambda: MessageSerializer(instance=conversation, context={'user': user}).data)()
    # Add the messageType and type
    serialized_conversation['messageType'] = "newConversation"
    serialized_conversation['type'] = "new_conversation"
    await send_ws_msg_to_user(user.id, **serialized_conversation)

# ==============================================================================
#     TOURNAMENT FUNCTIONS
# ==============================================================================
def send_ws_tournament_msg(tournament_id, type_camel, type_snake, message, **json_details):
    """ Those messages will be send to the tournament channel to update the tournament lobby """
    tournament_id_name = f"{PRE_GROUP_TOURNAMENT}{tournament_id}"
    async_to_sync(channel_layer.group_send)(
    tournament_id_name,
    {
        "messageType": type_camel,
        "type": type_snake,
        "tournamentId": tournament_id,
        "message": message,
        **json_details
    })
    logging.info(f"Message sent to tournament {tournament_id} channel ({tournament_id_name}): {message}")

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