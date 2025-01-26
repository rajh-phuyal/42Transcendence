from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import ConversationMember
import logging
User = get_user_model()
channel_layer = get_channel_layer()

# channel_name is the WebSocket connection ID for a user
# group_name is the conversation ID
@sync_to_async
def setup_all_conversations(user, channel_name, intialize=True):
    logging.info("MODE: %d, Configuring conversations for user: %s with channel_name: %s", intialize, user, channel_name)
    # Get all conversation IDs where the user is a member
    conversation_memberships = ConversationMember.objects.filter(user=user)
    for membership in conversation_memberships:
        group_name = f"conversation_{membership.conversation.id}"
        if intialize:
            async_to_sync(channel_layer.group_add)(group_name, channel_name)
            logging.info(f"\tAdded user {user} to group {group_name}")
        else:
            async_to_sync(channel_layer.group_discard)(group_name, channel_name)
            logging.info(f"\tRemoved user {user} from group {group_name}")

async def broadcast_message(message):
    group_name = f"conversation_{message.conversation.id}"
    logging.info(f"Broadcasting to group {group_name} from user {message.user}: {message.content}")
    await channel_layer.group_send(
        group_name,
        {
            "type": "chat_message",
            "messageType": "chat",
            "conversationId": message.conversation.id,
            "messageId": message.id,
            "userId": message.user.id,
            "username": message.user.username,
            "avatar": message.user.avatar_path,
            "content": message.content,
            "createdAt": message.created_at.isoformat(), #TODO: Issue #193
            "seenAt": message.seen_at.isoformat() if message.seen_at else None #TODO: Issue #193
        }
    )

@sync_to_async
def send_total_unread_counter(user_id):
    from services.websocket_utils import send_message_to_user
    conversation_memberships = ConversationMember.objects.filter(user=user_id)
    chat_unread_counter = 0
    for membership in conversation_memberships:
        chat_unread_counter += membership.unread_counter
    msg_data = {
        "type": "update_badge",
        "messageType": "updateBadge",
        "what": "all",
        "value": chat_unread_counter
    }
    logging.info("Sending the '%s' message for '%s' to the user '%s' with value '%s'", msg_data['type'], msg_data['what'], user_id, msg_data['value'])
    async_to_sync(send_message_to_user)(user_id, **msg_data)

@sync_to_async
def send_conversation_unread_counter(user_id, conversation_id):
    from services.websocket_utils import send_message_to_user
    unread_count = ConversationMember.objects.get(user=user_id, conversation=conversation_id).unread_counter
    msg_data = {
        "type": "update_badge",
        "messageType": "updateBadge",
        "what": "conversation",
        "id": conversation_id,
        "value": unread_count
    }
    logging.info("Sending the '%s' message for '%s' to the user '%s' with value '%s'", msg_data['type'], msg_data['what'], user_id, msg_data['value'])
    async_to_sync(send_message_to_user)(user_id, **msg_data)
