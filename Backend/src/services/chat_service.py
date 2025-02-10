from django.contrib.auth import get_user_model
from django.db.models import F

from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import ConversationMember
import logging
User = get_user_model()
channel_layer = get_channel_layer()


# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def broadcast_chat_message(message):
    # TODO: here we need to parse the message maybe via serializer?
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

    # TODO: check if still needed
    #await send_conversation_unread_counter(other_user_member.id, conversation_id)
    #await send_total_unread_counter(other_user_member.id)

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
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
    #logging.info("Sending the '%s' message for '%s' to the user '%s' with value '%s'", msg_data['type'], msg_data['what'], user_id, msg_data['value'])
    async_to_sync(send_message_to_user)(user_id, **msg_data)

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
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
    #logging.info("Sending the '%s' message for '%s' to the user '%s' with value '%s'", msg_data['type'], msg_data['what'], user_id, msg_data['value'])
    async_to_sync(send_message_to_user)(user_id, **msg_data)
