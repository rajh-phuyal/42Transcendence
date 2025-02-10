# Basics
import logging
# Django
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from rest_framework import status
# Services
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
# Chat
from chat.models import Conversation, Message, ConversationMember
from core.exceptions import BarelyAnException
channel_layer = get_channel_layer()

class LastSeenMessage:
    def __init__(self, created_at, sender):
        self.id = None
        self.user = sender
        self.created_at = created_at
        self.seen_at = None
        self.content = _("We know that you haven't seen the messages below...")

# TODO: NEW SHOULD BE USED EVERYWHERE
def validate_conversation_membership(user, conversation):
    """ Accepts user and conversation instances or IDs """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    if isinstance(conversation, int):
        conversation = Conversation.objects.get(id=conversation)
    if user.id == USER_ID_OVERLORDS:
        return
    try:
        return ConversationMember.objects.get(conversation=conversation, user=user)
    except ConversationMember.DoesNotExist:
        raise BarelyAnException(_('You are not a member of this conversation'), status_code=status.HTTP_403_FORBIDDEN)

# TODO: NEW SHOULD BE USED EVERYWHERE
def get_other_user(user, conversation):
    """ Accepts user and conversation instances or IDs
        Returns the other user instance in the conversation """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    if isinstance(conversation, int):
        conversation = Conversation.objects.get(id=conversation)
    if user.id == USER_ID_OVERLORDS:
        logging.error("get_other_user() doesnt work with account overlords!")
        return

    other_user = ConversationMember.objects.filter(conversation=conversation).exclude(user=user).first().user
    return other_user





# TODO old stuff below!!!


# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def mark_all_messages_as_seen_sync(user, conversation):
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
            logging.info(f"Marked {len(unread_messages)} messages as seen by user {user} in conversation {conversation}")
            # Update unread counter
            conversation_member = ConversationMember.objects.select_for_update().get(conversation_id=conversation, user=user)
            conversation_member.unread_counter = 0
            conversation_member.save(update_fields=['unread_counter'])
    except Exception as e:
        logging.error(f"Error marking messages as seen: {e}")

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
@database_sync_to_async
def mark_all_messages_as_seen_async(user_id, conversation_id):
    mark_all_messages_as_seen_sync(user_id, conversation_id)



# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def get_conversation_id(user1, user2):
    user_conversations = ConversationMember.objects.filter(
        user=user1.id,
        conversation__is_group_conversation=False,
    ).values_list('conversation_id', flat=True)

    other_user_conversations = ConversationMember.objects.filter(
        user=user2.id,
        conversation__is_group_conversation=False
    ).values_list('conversation_id', flat=True)

    common_conversations = set(user_conversations).intersection(other_user_conversations)

    if common_conversations:
        return common_conversations.pop()
    return None

# Create a conversation between two users
    # create a conversation
    # create two conversation members
    # create a message
    # add the conversation to the user's WebSocket groups
    # send a message to the user's WebSocket group
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def create_conversation(user1, user2, initialMessage, creator = None):
    from services.websocket_utils import send_message_to_user_sync

    # Start a transaction to make sure all database operations happen together
    with transaction.atomic():
        # Create the Conversation
        new_conversation = Conversation.objects.create()
        if creator == user1:
            ConversationMember.objects.create(user=user1, conversation=new_conversation)
        else:
            ConversationMember.objects.create(user=user1, conversation=new_conversation, unread_counter=1)

        if creator == user2:
            ConversationMember.objects.create(user=user2, conversation=new_conversation)
        else:
            ConversationMember.objects.create(user=user2, conversation=new_conversation, unread_counter=1)

        overloards = User.objects.get(id=USER_ID_OVERLORDS)
        if not creator:
            creator = overloards
        initialMessageObject = Message.objects.create(user=creator, conversation=new_conversation, content=initialMessage)

    # TODO: need to send the **S,userIdStarter** message to the user aka the beginning of the conversation thing
    # Adding the conversation to the user's WebSocket groups (if they are logged in)
    group_name = f"conversation_{new_conversation.id}"
    channel_name_user1 = cache.get(f'user_channel_{user1.id}', None)
    if channel_name_user1:
        async_to_sync(channel_layer.group_add)(group_name, channel_name_user1)
    channel_name_user2 =  cache.get(f'user_channel_{user2.id}', None)
    if channel_name_user2:
        async_to_sync(channel_layer.group_add)(group_name, channel_name_user2)

    # TODO: this should be done by create_message
    # Sending a message to user1
    message={
        "messageType": "newConversation",
        "type": "new_conversation",
        "conversationId": new_conversation.id,
        "isGroupChat": new_conversation.is_group_conversation,
        "isEditable": new_conversation.is_editable,
        "conversationName": user2.username,
        "conversationAvatar": user2.avatar_path,
        "unreadCounter": 1,
        "online": True,
        "lastUpdate": initialMessageObject.created_at.isoformat(), #TODO: Issue #193
        "isEmpty": False
    }
    send_message_to_user_sync(user1.id, **message)

    # Sending a message to user2
    message={
        "messageType": "newConversation",
        "type": "new_conversation",
        "conversationId": new_conversation.id,
        "isGroupChat": new_conversation.is_group_conversation,
        "isEditable": new_conversation.is_editable,
        "conversationName": user1.username,
        "conversationAvatar": user1.avatar_path,
        "unreadCounter": 1,
        "online": True,
        "lastUpdate": initialMessageObject.created_at.isoformat(), #TODO: Issue #193
        "isEmpty": False
    }
    send_message_to_user_sync(user2.id, **message)

    # TODO: THIS also will be done by create_message
    if creator == user1:
        async_to_sync(send_total_unread_counter)(user2.id)
        async_to_sync(send_conversation_unread_counter)(user2.id, new_conversation.id)
    elif creator == user2:
        async_to_sync(send_total_unread_counter)(user1.id)
        async_to_sync(send_conversation_unread_counter)(user1.id, new_conversation.id)

    return new_conversation

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
