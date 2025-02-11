from django.contrib.auth import get_user_model
from django.db.models import F


from channels.layers import get_channel_layer
from chat.models import ConversationMember
import logging
User = get_user_model()
channel_layer = get_channel_layer()
from services.websocket_utils import send_ws_msg_to_user



















# TODO: OLD CODE BELOW



# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def broadcast_chat_message(message):
    # TODO: here we need to parse the message maybe via serializer?
    

    # TODO: check if still needed
    #await send_conversation_unread_counter(other_user_member.id, conversation_id)
    #await send_total_unread_counter(other_user_member.id)

