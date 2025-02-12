from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from user.constants import AVATAR_OVERLORDS, USERNAME_OVERLORDS, USER_ID_OVERLORDS
from services.constants import PRE_CONVERSATION
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone
from chat.serializers import MessageSerializer
from django.core.cache import cache
from services.constants import PRE_USER_CHANNEL
import logging, json
from chat.models import ConversationMember, Message, Conversation
from asgiref.sync import async_to_sync
from user.models import User


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

# Basic function to send a message to a user via WebSocket
async def send_ws_msg_to_user(user_id, **message):
    channel_name =  cache.get(f'{PRE_USER_CHANNEL}{user_id}')
    if channel_name:
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user_id}.")

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

async def send_ws_info_msg(user_id, content):
    message_dict = {
        "messageType": "info",
        "type": "info",
        "message": content
    }
    json_message = json.dumps(message_dict)
    await send_ws_msg_to_user(user_id, **json_message)

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
    chat_unread_counter = 0
    for membership in conversation_memberships:
        chat_unread_counter += membership.unread_counter
    msg_data = {
        "messageType": "updateBadge",
        "type": "update_badge",
        "what": "all",
        "value": chat_unread_counter
    }
    async_to_sync(send_ws_msg_to_user)(user_id, **msg_data)

async def send_ws_chat(message_object):
    logging.info(f"start to serialize message: {message_object}")
    serialized_message = await sync_to_async(lambda: MessageSerializer(instance=message_object).data)()
    logging.info(f"serialized message: {serialized_message}")
    # Send to conversation channel
    group_name = f"{PRE_CONVERSATION}{message_object.conversation.id}"
    await channel_layer.group_send(group_name, serialized_message)

async def send_ws_other():
    ...

async def send_ws_new_conversation():
    ...
