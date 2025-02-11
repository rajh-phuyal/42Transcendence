# Basics
import logging
# Django
from channels.layers import get_channel_layer
from django.core.cache import cache
from services.constants import PRE_USER_CHANNEL
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from chat.models import ConversationMember



@sync_to_async
def send_ws_msg_unread_total(user_id):
    from services.websocket_handler_main import send_message_to_user
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
    async_to_sync(send_ws_msg_to_user)(user_id, **msg_data)

@sync_to_async
def send_ws_msg_unread_conversation(user_id, conversation_id):
    from services.websocket_handler_main import send_message_to_user
    unread_count = ConversationMember.objects.get(user=user_id, conversation=conversation_id).unread_counter
    msg_data = {
        "type": "update_badge",
        "messageType": "updateBadge",
        "what": "conversation",
        "id": conversation_id,
        "value": unread_count
    }
    #logging.info("Sending the '%s' message for '%s' to the user '%s' with value '%s'", msg_data['type'], msg_data['what'], user_id, msg_data['value'])
    async_to_sync(send_ws_msg_to_user)(user_id, **msg_data)