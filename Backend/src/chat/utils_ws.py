# Basics
import logging
# Django
from django.utils.translation import gettext as _
from django.db import transaction
from django.db.models import Q, F
from channels.db import database_sync_to_async
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
from asgiref.sync import async_to_sync, sync_to_async
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
from chat.utils import mark_all_messages_as_seen_async, create_conversation,validate_conversation_membership, get_other_user

# TODO: NEW SHOULD BE USED EVERYWHERE
@database_sync_to_async
def validate_conversation_membership_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    validate_conversation_membership(user, conversation)

# TODO: NEW SHOULD BE USED EVERYWHERE
@database_sync_to_async
def get_other_user_async(user, conversation):
    """ Accepts user and conversation instances or IDs """
    return get_other_user(user, conversation)





























# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def create_chat_message(sender, conversation_id, content):
    # Validate conversation exists & user is a member of the conversation
    logging.info(f"Creating a message in conversation {conversation_id} from {sender.username}: '{content}'")
    validate_conversation_membership_async(sender, conversation_id)
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

            async_to_sync(broadcast_chat_message)(message)
    except Exception as e:
        logging.error(f"TODO: eeror msg is shit Error updating unread messages count for user {other_user_member.user}: {e}")
    return message

# Main fucntion of incoming chat message via WS
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def process_incoming_chat_message(consumer, user, text):
    from Backend.src.services.websocket_handler_main import check_message_keys
    from user.utils_relationship import is_blocked
    message = check_message_keys(text, mandatory_keys=['conversationId', 'content'])
    conversation_id = message.get('conversationId')
    content = message.get('content', '').strip()
    other_user = await get_other_user_async(user, conversation_id)
    logging.info(f"User {user} to conversation {conversation_id}: '{content}'")

    # Content cant be empty
    if not content:
        await send_temporary_info_msg(user.id, conversation_id, _("Message content cannot be empty"))
        return

    # Check if content starts with a "/"
    # This means that the message was a command and therefore was handled
    if await check_if_msg_is_cmd(user, other_user, conversation_id, content):
        return

    # Check if user is blocked by other member
    if await sync_to_async(is_blocked)(user, other_user):
        await send_temporary_info_msg(user.id, conversation_id, _("You have been blocked by this user"))
        return

    # Check if the message contains an @username
    await check_if_msg_contains_username(user, other_user, conversation_id, content)

    # Do db operations and send it
    await sync_to_async(create_chat_message)(user, conversation_id, content)

# FE tells backend that user has seen a conversation
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
async def process_incoming_seen_message(self, user, text):
    from Backend.src.services.websocket_handler_main import check_message_keys
    message = check_message_keys(text, mandatory_keys=['conversationId'])
    conversation_id = message.get('conversationId')
    await validate_conversation_membership_async(user, conversation_id)
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
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def create_overloards_pm(userA, userB, content, sendIt=True):
    logging.info(f"Creating a overloards message in conversation of {userA.username} and {userB.username}: '{content}'")
    conversation_id = get_conversation_id(userA, userB)
    if conversation_id:
        conversation = Conversation.objects.get(id=conversation_id)
    else:
        conversation = create_conversation(userA, userB, content).id
    overloards = User.objects.get(id=USER_ID_OVERLORDS)
    create_chat_message(overloards, conversation.id, content)