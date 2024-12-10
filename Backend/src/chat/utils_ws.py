from django.core.cache import cache
from django.db import transaction
from user.models import User
from chat.models import Message, ConversationMember, Conversation
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from user.exceptions import BlockingException
import json
from user.constants import USER_ID_OVERLOARDS
from django.db.models import Q
from user.utils_relationship import is_blocked
import logging
from channels.db import database_sync_to_async
from chat.utils import mark_all_messages_as_seen_async
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
from asgiref.sync import sync_to_async

@database_sync_to_async
def validate_user_is_member_of_conversation(user, conversation_id):
    # Validate conversation exists & user is a member of the conversation
    conversation_member_entry =  ConversationMember.objects.filter(conversation_id=conversation_id, user=user).first()
    if not conversation_member_entry:
        raise BarelyAnException(_("Conversation not found or user is not a member of the conversation"))
    return conversation_member_entry


# Wrap the synchronous database operations with sync_to_async
@database_sync_to_async
def create_message(user, conversation_id, content):

    # Validate conversation exists & user is a member of the conversation
    validate_user_is_member_of_conversation(user, conversation_id)
    conversation = Conversation.objects.get(id=conversation_id)
    other_user_member = (
        ConversationMember.objects
            .filter(conversation=conversation_id)
            .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLOARDS))
            .first() #TODO: #204 Groupchat remove the first() and return the list
        )
    
    # Check if user is blocked by other member (if not group chat)
    if not conversation.is_group_conversation:
        if is_blocked(user, other_user_member.user):
            raise BlockingException(_("You have been blocked by this user"))
    
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
            other_user_member = (
                ConversationMember.objects
                    .select_for_update()
                    .filter(conversation=conversation)
                    .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLOARDS))
                    .first() #TODO: #204 Groupchat remove the first() and return the list
                )
            other_user_member.unread_counter = unread_messages_count
            other_user_member.save(update_fields=['unread_counter'])
            logging.info("Setting unread messages count for user %s to %s", other_user_member.user, unread_messages_count)

    except Exception as e:
        logging.error(f"Error updating unread messages count for user {other_user_member.user}: {e}")
    return message, other_user_member.user.id

# Websocket message
async def process_incoming_chat_message(consumer, user, text):
    from services.websocket_utils import parse_message
    message = parse_message(text, mandatory_keys=['conversationId', 'content'])
    conversation_id = message.get('conversationId')
    content = message.get('content')
    logging.info(f"User {user} to conversation {conversation_id}: '{content}'")
    
    # Do db operations
    new_message, other_user_member_id = await create_message(user, conversation_id, content)

    # Update the badges
    await send_conversation_unread_counter(other_user_member_id, conversation_id)
    await send_total_unread_counter(other_user_member_id)

    return new_message

# FE tells backend that user has seen a conversation
async def process_incoming_seen_message(self, user, text):
    from services.websocket_utils import parse_message
    message = parse_message(text, mandatory_keys=['conversationId'])
    conversation_id = message.get('conversationId')
    await validate_user_is_member_of_conversation(user, conversation_id)
    await mark_all_messages_as_seen_async(user.id, conversation_id)
    await send_conversation_unread_counter(user.id, conversation_id)
    await send_total_unread_counter(user.id)