from services.chat_service import setup_all_conversations, broadcast_message, setup_all_badges
from django.core.cache import cache
from services.websocket_utils import send_message_to_user
from django.db import transaction
from user.models import User
from chat.models import Message, ConversationMember
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from user.exceptions import BlockingException
import json
from user.constants import USER_ID_OVERLOARDS
from django.db.models import Q
from user.utils_relationship import is_blocked
import logging
from core.decorators import barely_handle_ws_exceptions
from channels.db import database_sync_to_async
from chat.utils import mark_all_messages_as_seen
from asgiref.sync import sync_to_async

# Wrap the synchronous database operations with sync_to_async
@database_sync_to_async
def create_message(user, conversation_id, content):

    # Validate conversation exists & user is a member of the conversation
    conversation_member_entry =  ConversationMember.objects.filter(conversation_id=conversation_id, user=user).first()
    if not conversation_member_entry:
        raise BarelyAnException(_("Conversation not found or user is not a member of the conversation"))
    conversation = conversation_member_entry.conversation
    other_user_member = (
        ConversationMember.objects
            .filter(conversation=conversation)
            .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLOARDS))
            .first() #TODO: Groupchat remove the first() and return the list
        )
    
    # Check if user is blocked by other member (if not group chat)
    if not conversation.is_group_conversation:
        if is_blocked(user, other_user_member.user):
            raise BlockingException(detail='You have been blocked by this user.')
    
    try:
        with transaction.atomic():
            # Create message
            message = Message.objects.create(
                user=user,
                conversation=conversation,
                content=content,
            )
    
            # Update unread message count for the other user
            unread_messages_count = Message.objects.filter(
                conversation=conversation,
                user=user,
                seen_at__isnull=True
            ).count()
            other_user_member.select_for_update().update(unread_messages_count=unread_messages_count)
            # Sent this updated value to the frontend:
            setup_all_badges(user.id)

    except Exception as e:
        logging.error(f"Error updating unread messages count for user {other_user_member.user}: {e}")
    return message
    
def parse_message(text):
    text_json = json.loads(text)
    conversation_id = text_json.get('conversationId', '')
    if not conversation_id:
        raise BarelyAnException(_("key 'conversationId' is required for websocket message type 'chat'"))
    content = text_json.get('content', '')
    if not content:
        raise BarelyAnException(_("key 'content' is required for websocket message type 'chat'"))
    return conversation_id, content

# Websocket message
async def process_incoming_chat_message(self, user, text):
    conversation_id, content = parse_message(text)
    logging.info(f"User {user} to conversation {conversation_id}: '{content}'")
    
    # Do db operations
    return await create_message(user, conversation_id, content)

@sync_to_async
def validate_user_is_member_of_conversation(user, conversation_id):
    # Validate conversation exists & user is a member of the conversation
    conversation_member_entry =  ConversationMember.objects.filter(conversation_id=conversation_id, user=user).first()
    if not conversation_member_entry:
        raise BarelyAnException(_("Conversation not found or user is not a member of the conversation"))

async def process_incoming_seen_message(self, user, text):
    text_json = json.loads(text)
    conversation_id = text_json.get('conversationId', '')
    if not conversation_id:
        raise BarelyAnException(_("key 'conversationId' is required for websocket message type 'seen'"))
    await validate_user_is_member_of_conversation(user, conversation_id)
    await mark_all_messages_as_seen(user.id, conversation_id)