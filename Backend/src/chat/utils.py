# Basics
import logging
# Django
from django.db import transaction
from django.utils.translation import gettext as _
from channels.layers import get_channel_layer
from rest_framework import status
# Core
from core.exceptions import BarelyAnException
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
# Chat
from chat.models import Conversation, Message, ConversationMember
channel_layer = get_channel_layer()

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

def get_other_user(user, conversation):
    """
    Accepts user and conversation instances or IDs
    Returns the other user instance in the conversation
    """
    if isinstance(user, int):
        user = User.objects.get(id=user)
    if isinstance(conversation, int):
        conversation = Conversation.objects.get(id=conversation)
    if user.id == USER_ID_OVERLORDS:
        logging.error("get_other_user() doesnt work with account overlords!")
        return

    other_user = ConversationMember.objects.filter(conversation=conversation).exclude(user=user).first().user
    return other_user
