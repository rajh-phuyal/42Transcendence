# Basics
import logging
# Django
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
# Core
from core.exceptions import BarelyAnException
# Services
from services.send_ws_msg import send_ws_badge, send_ws_badge_all, send_ws_chat
# Chat
from chat.models import ConversationMember, Message
from chat.conversation_utils import get_or_create_conversation

def create_msg_db(sender, conversation, content):
    """
    Creates a message in the database and updates the unread message count
    for all conversation_member entries (except the sender).
    """
    content = content.strip()
    if not content:
        raise BarelyAnException("Message content is empty.")
    try:
        with transaction.atomic():
            # Create message
            message = Message.objects.create(
                user=sender,
                conversation=conversation,
                content=content
            )
            logging.info(f"Message created: {message}")
            # Update unread message count for users (except the sender)
            ConversationMember.objects.filter(
                conversation=conversation
            ).exclude(user=sender).update(unread_counter=F('unread_counter') + 1)
    except Exception as e:
        logging.error(f"Error creating message on db: {e}")
    return message

def create_and_send_overloards_pm(userA, userB, content):
    """
    Whenever the backend needs to send a message to a conversation it will be
    from the overlords to a conversation between two users.
    This function will create a message in the database and send it to the frontend
    also updating the unread message count for all conversation_member entries.
    """
    conversation = get_or_create_conversation(userA, userB)
    message = create_msg_db(User.objects.get(id=USER_ID_OVERLORDS), conversation, content)
    async_to_sync(send_ws_badge)(userA.id, conversation.id)
    async_to_sync(send_ws_badge)(userB.id, conversation.id)
    async_to_sync(send_ws_badge_all)(userA.id)
    async_to_sync(send_ws_badge_all)(userB.id)
    async_to_sync(send_ws_chat)(message)

@database_sync_to_async
def mark_all_messages_as_seen_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    mark_all_messages_as_seen(user, conversation)

def mark_all_messages_as_seen(user, conversation):
    """ Accepts user and conversation instances or IDs """
    if not isinstance(user, int):
        user = user.id
    if not isinstance(conversation, int):
        conversation = conversation.id

    try:
        with transaction.atomic():
            unread_messages = (
                Message.objects
                .select_for_update()
                .filter(conversation_id=conversation, seen_at__isnull=True)
                .exclude(user=user)
            )

            # Update messages
            unread_messages.update(seen_at=timezone.now()) #TODO: Issue #193
            # Update unread counter
            conversation_member = ConversationMember.objects.select_for_update().get(conversation_id=conversation, user=user)
            conversation_member.unread_counter = 0
            conversation_member.save(update_fields=['unread_counter'])
    except Exception as e:
        logging.error(f"Error marking messages as seen: {e}")
    async_to_sync(send_ws_badge)(user, conversation)
    async_to_sync(send_ws_badge_all)(user)