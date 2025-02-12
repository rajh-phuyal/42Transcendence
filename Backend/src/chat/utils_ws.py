# Basics
import logging
# Django
from django.utils.translation import gettext as _
from django.db import transaction
from django.db.models import F
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
# Core
from core.exceptions import BarelyAnException
# Services
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
from user.exceptions import BlockingException
# Chat
from chat.models import Message, ConversationMember, Conversation
from chat.utils import mark_all_messages_as_seen_async, create_conversation,validate_conversation_membership, get_other_user

# TODO: NEW SHOULD BE USED EVERYWHERE # TODO: REMOVE WHEN FINISHED #284
@database_sync_to_async
def validate_conversation_membership_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    validate_conversation_membership(user, conversation)

# TODO: NEW SHOULD BE USED EVERYWHERE # TODO: REMOVE WHEN FINISHED #284
@database_sync_to_async
def get_other_user_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    return get_other_user(user, conversation)
































# FE tells backend that user has seen a conversation
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def process_incoming_seen_message(self, user, text):
    from services.websocket_handler_main import check_message_keys
    message = check_message_keys(text, mandatory_keys=['conversationId'])
    conversation_id = message.get('conversationId')
    await validate_conversation_membership_async(user, conversation_id)
    await mark_all_messages_as_seen_async(user.id, conversation_id)
    # TODO: uncomment: await send_conversation_unread_counter(user.id, conversation_id)
    # TODO: uncomment: await send_total_unread_counter(user.id)

