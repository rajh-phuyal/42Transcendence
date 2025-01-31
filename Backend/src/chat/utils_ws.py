from django.core.cache import cache
from django.db import transaction
from chat.constants import ALLOWED_MSG_CMDS_PATTERNS
from user.models import User
from chat.models import Message, ConversationMember, Conversation
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from user.exceptions import BlockingException
from user.constants import USER_ID_OVERLORDS
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
            .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLORDS))
            .first()
        )

    # Check if user is blocked by other member (if not group chat)
    if not conversation.is_group_conversation:
        if is_blocked(user, other_user_member.user):
            raise BlockingException(_("You have been blocked by this user"))

    # Check if content is empty
    if not content:
        raise BarelyAnException(_("Message content cannot be empty"))

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
                    .exclude(Q(user=user) | Q(user_id=USER_ID_OVERLORDS))
                    .first()
                )
            other_user_member.unread_counter = unread_messages_count
            other_user_member.save(update_fields=['unread_counter'])
            logging.info("Setting unread messages count for user %s to %s", other_user_member.user, unread_messages_count)

    except Exception as e:
        logging.error(f"Error updating unread messages count for user {other_user_member.user}: {e}")
    return message, other_user_member.user.id

# Valid commands in messaages are defined in ALLOWED_MSG_CMDS_PATTERNS
async def parse_message_cmd(user, conversation_id, content):
    logging.info("Checking for cmds in message: %s", content)

    if content.startswith("**"):
        logging.info("Message could contain cmd")

        # Parse the command
        try:
            for cmd_name, (patterns, args) in ALLOWED_MSG_CMDS_PATTERNS.items():
                for pattern in patterns:
                    match = pattern.match(content)
                    if match:
                        logging.info(f"Message contains valid cmd: {cmd_name}")

                        # Extract values dynamically
                        values = {args[i]: match.group(i + 1) for i in range(len(args))}

                        logging.info(f"Extracted values: {values}")

                        # Execute the command with extracted values
                        if cmd_name == "invite":
                            logging.info("Executing invite cmd with args: %s", values)
                            # TODO conitnue here!!!!!
                            asdasdsad
                            # map_name_to_number
                            #await create_game(values["powerups"], values["map"], user, conversation_id)

                        return user, content
        except Exception as e:
            logging.error(f"Error parsing: {e}")
            logging.info("Send info msg")
            #await send_cmd_info_msg(user.id, conversation_id)
    logging.info("Send info msg")
    return user, content

# Websocket message
async def process_incoming_chat_message(consumer, user, text):
    from services.websocket_utils import parse_message
    message = parse_message(text, mandatory_keys=['conversationId', 'content'])
    conversation_id = message.get('conversationId')
    content = message.get('content', '').strip()
    logging.info(f"User {user} to conversation {conversation_id}: '{content}'")

    # Check if content contains a cmd
    user, content = await parse_message_cmd(user, conversation_id, content)

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
