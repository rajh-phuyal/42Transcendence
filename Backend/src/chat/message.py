# Basics
# Django
from django.db import transaction
from django.db.models import F
# User
from user.models import User
# Chat
import logging
from chat.models import Conversation, ConversationMember, Message
from chat.utils import validate_conversation_membership, get_other_user
from chat.serializers import MessageSerializer
from services.websocket_utils import send_ws_msg_unread_conversation, send_ws_msg_unread_total
from services.constants import PRE_CONVERSATION


# This is the main function for processing a message
# It will be called from everywhere and contains:
# - A message.content which is already parsed before
# - A sender which is the user who sent the message
# - A conversation_id which is the conversation the message is sent to
#
# This function will:
# - Validate the conversation exists
# - Validate the user is a member of the conversation (or the overlords)
# - Create the message insance and save it to the database
# - Send the update badge count to all users in the conversation (except the sender)
# - Serialize the message and send it to the frontend
def outgoing_chat_msg_main(sender, conversation_id, parsedContent):
    """ Accepts sender instances or IDs """
    if isinstance(sender, int):
        sender = User.objects.get(id=sender)

    conversation = Conversation.objects.get(id=conversation_id)
    validate_conversation_membership(sender, conversation)

    message = None
    with transaction.atomic():
        message = Message.objects.create(
            user=sender,
            conversation=conversation,
            content=parsedContent
        )
        message.save()
        ConversationMember.objects.filter(
                conversation=conversation
            ).exclude(user=sender).update(unread_counter=F('unread_counter') + 1)

    if not message:
        logging.error(f"Failed to create message in conversation {conversation_id} from {sender.username}: '{parsedContent}'")
        return

    # Send the badge update to all users in the conversation except the sender
    members = ConversationMember.objects.filter(conversation=conversation).exclude(user=sender)
    for member in members:
        send_ws_msg_unread_conversation(member.user.id, conversation_id)
        send_ws_msg_unread_total(member.user.id)

    # Send the message to the frontend
    serializer = MessageSerializer(message)
    if serializer.is_valid():
        message = serializer.data
    else:
        logging.error(f"Failed to serialize message: {serializer.errors}")
        return

    group_name = f"{PRE_CONVERSATION}{message.conversation.id}"
    logging.info(f"Broadcasting to group {group_name} from user {message.user}: {message.content}")
    await channel_layer.group_send(group_name, message)