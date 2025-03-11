# Basics
import logging
# Django
from django.utils.translation import gettext as _
from django.db import transaction
# Servies
from services.channel_groups import update_client_in_group
from services.constants import PRE_GROUP_CONVERSATION
from asgiref.sync import async_to_sync
# User
from user.constants import USER_ID_AI, USER_ID_FLATMATE
from user.models import User
# Services
from services.send_ws_msg import send_ws_new_conversation
from services.chat_bots import send_message_with_delay
# Chat
from chat.models import Conversation, ConversationMember

def get_conversation_id(user1, user2):
    """
    This function will return the conversation ID between two users.
    If no conversation exists, it will return None.
    Argumuments can be instances or IDs of the users.
    """
    if isinstance(user1, int):
        user1 = User.objects.get(id=user1)
    if isinstance(user2, int):
        user2 = User.objects.get(id=user2)

    # Conversations of user1
    user_conversations = ConversationMember.objects.filter(
        user=user1.id,
        conversation__is_group_conversation=False,
    ).values_list('conversation_id', flat=True)

    # Conversations of user2
    other_user_conversations = ConversationMember.objects.filter(
        user=user2.id,
        conversation__is_group_conversation=False
    ).values_list('conversation_id', flat=True)

    # Common conversations
    common_conversations = set(user_conversations).intersection(other_user_conversations)

    if common_conversations:
        return common_conversations.pop()
    return None

def get_or_create_conversation(user1, user2):
    """
    This function will always return a valid conversation between two users.
    If it not exists, it will create a new
    Argumuments can be instances or IDs of the users.
    """
    if isinstance(user1, int):
        user1 = User.objects.get(id=user1)
    if isinstance(user2, int):
        user2 = User.objects.get(id=user2)
    conversation_id = get_conversation_id(user1, user2)
    if conversation_id:
        return Conversation.objects.get(id=conversation_id)
    else:
        return create_conversation(user1, user2)

def create_conversation(user1, user2):
    """
    This function will create a conversation between two users.
    Should only be called from function 'get_or_create_conversation'
    Note: This function does NOT check if a conversation already exists.
    """
    from chat.message_utils import create_and_send_overloards_pm
    # Create conversation and Members
    with transaction.atomic():
        conversation = Conversation.objects.create()
        conversation.save()
        member1 = ConversationMember.objects.create(conversation=conversation, user=user1)
        member2 = ConversationMember.objects.create(conversation=conversation, user=user2)
        member1.save()
        member2.save()
    # Add the members to the channel
    async_to_sync(update_client_in_group)(user1, conversation.id, PRE_GROUP_CONVERSATION, add=True)
    async_to_sync(update_client_in_group)(user2, conversation.id, PRE_GROUP_CONVERSATION, add=True)
    # Send the new conversation ws message (in case the user has chat view open)
    async_to_sync(send_ws_new_conversation)(user1, conversation)
    async_to_sync(send_ws_new_conversation)(user2, conversation)
    # Create the start of conversation message
    create_and_send_overloards_pm(user1, user2, f"**S,{user1.id},{user2.id}**")
    # If it is AI or Flatmate send a response
    if user1.id in [USER_ID_AI, USER_ID_FLATMATE]:
        async_to_sync(send_message_with_delay)(user1, user2, 0, _("Hello there!"))
    if user2.id in [USER_ID_AI, USER_ID_FLATMATE]:
        async_to_sync(send_message_with_delay)(user2, user1, 0, _("Hello there!"))
    return conversation