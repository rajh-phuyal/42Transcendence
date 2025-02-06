# Basics
import logging
# Django
from django.utils.translation import gettext as _
from django.db import transaction
from django.db.models import Q, F
from channels.db import database_sync_to_async
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
# Core
from core.exceptions import BarelyAnException
# Services
from services.chat_service import broadcast_chat_message
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
from user.exceptions import BlockingException
# Chat
from chat.models import Message, ConversationMember, Conversation
from chat.parse_incoming_message import check_if_msg_is_cmd, check_if_msg_contains_username, send_temporary_info_msg
from chat.utils import mark_all_messages_as_seen_async, get_conversation_id, create_conversation

@database_sync_to_async
def validate_user_is_member_of_conversation(user, conversation_id):
    # Validate conversation exists & user is a member of the conversation
    conversation = Conversation.objects.get(id=conversation_id) # This will raise an exception if the conversation does not exist
    # If the user is the overlord, he can access all conversations
    if user.id == USER_ID_OVERLORDS:
        return
    conversation_member_entry =  ConversationMember.objects.filter(conversation_id=conversation_id, user=user).first()
    if not conversation_member_entry:
        raise BarelyAnException(_("Conversation not found or user is not a member of the conversation"))
    return

@database_sync_to_async
def get_other_user_member(user, conversation_id):
    other_user_member = (
        ConversationMember.objects
            .filter(conversation=conversation_id)
            .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLORDS))
            .first()
        ).user
    return other_user_member

def get_conversation_users(conversation_id):
    return ConversationMember.objects.filter(conversation_id=conversation_id).values_list('user', flat=True)

def create_chat_message(sender, conversation_id, content):
    # Validate conversation exists & user is a member of the conversation
    logging.info(f"Creating a message in conversation {conversation_id} from {sender.username}: '{content}'")
    validate_user_is_member_of_conversation(sender, conversation_id)
    conversation = Conversation.objects.get(id=conversation_id)
    logging.info(f"Conversation {conversation_id} found: {conversation}")
    try:
        with transaction.atomic():
            # Create message
            message = Message.objects.create(
                user=sender,
                conversation=conversation,
                content=content,
            )
            logging.info(f"Message created: {message}")
            # Update unread message count for users (except the sender)
            ConversationMember.objects.filter(
                conversation=conversation
            ).exclude(user=sender).update(unread_counter=F('unread_counter') + 1)

            broadcast_chat_message(message)
    except Exception as e:
        logging.error(f"TODO: eeror msg is shit Error updating unread messages count for user {other_user_member.user}: {e}")
    return message

# Main fucntion of incoming chat message via WS
async def process_incoming_chat_message(consumer, user, text):
    from services.websocket_utils import check_message_keys
    from user.utils_relationship import is_blocked
    message = check_message_keys(text, mandatory_keys=['conversationId', 'content'])
    conversation_id = message.get('conversationId')
    content = message.get('content', '').strip()
    other_user_member = await get_other_user_member(user, conversation_id)
    logging.info(f"User {user} to conversation {conversation_id}: '{content}'")

    # Content cant be empty
    if not content:
        send_temporary_info_msg(user.id, conversation_id, _("Message content cannot be empty"))
        return

    # Check if content starts with a "/"
    # This means that the message was a command and therefore was handled
    if await check_if_msg_is_cmd(user, other_user_member, conversation_id, content):
        return

    # Check if user is blocked by other member
    if is_blocked(user, other_user_member):
        send_temporary_info_msg(user.id, conversation_id, _("You have been blocked by this user"))
        return

    # Check if the message contains an @username
    await check_if_msg_contains_username(user, other_user_member, conversation_id, content)

    # Do db operations
    # TODO: change since the function is now sync
    #new_message = await create_chat_message(user, other_user_member, conversation_id, content)

    # TODO: here we need to parse the message maybe via serializer?
    await broadcast_chat_message(new_message)

# FE tells backend that user has seen a conversation
async def process_incoming_seen_message(self, user, text):
    from services.websocket_utils import check_message_keys
    message = check_message_keys(text, mandatory_keys=['conversationId'])
    conversation_id = message.get('conversationId')
    await validate_user_is_member_of_conversation(user, conversation_id)
    await mark_all_messages_as_seen_async(user.id, conversation_id)
    await send_conversation_unread_counter(user.id, conversation_id)
    await send_total_unread_counter(user.id)

# This will be used to create a message in db.
# Shoulf be used by:
#   - creating game invites
#   - creating tournament invites
#   - changeing of friend requests
#   - profile page -> send message to user
#
# NOTE: If the conversation does not exist it will be created
def create_overloards_pm(userA, userB, content, sendIt=True):
    logging.info(f"Creating a overloards message in conversation of {userA.username} and {userB.username}: '{content}'")
    conversation_id = get_conversation_id(userA, userB)
    if conversation_id:
        conversation = Conversation.objects.get(id=conversation_id)
    else:
        conversation = create_conversation(userA, userB, content).id
    overloards = User.objects.get(id=USER_ID_OVERLORDS)
    create_chat_message(overloards, conversation.id, content)