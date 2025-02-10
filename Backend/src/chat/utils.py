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
# Services
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
# Chat
from chat.models import Conversation, Message, ConversationMember
channel_layer = get_channel_layer()

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def mark_all_messages_as_seen_sync(user_id, conversation_id):
    try:
        with transaction.atomic():
            unread_messages = (
                Message.objects
                .select_for_update()
                .filter(conversation_id=conversation_id, seen_at__isnull=True)
                .exclude(user=user_id)
            )

            # Update messages
            unread_messages.update(seen_at=timezone.now()) #TODO: Issue #193
            logging.info(f"Marked {len(unread_messages)} messages as seen by user {user_id} in conversation {conversation_id}")
            # Update unread counter
            conversation_member = ConversationMember.objects.select_for_update().get(conversation_id=conversation_id, user=user_id)
            conversation_member.unread_counter = 0
            conversation_member.save(update_fields=['unread_counter'])
    except Exception as e:
        logging.error(f"Error marking messages as seen: {e}")

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
@database_sync_to_async
def mark_all_messages_as_seen_async(user_id, conversation_id):
    mark_all_messages_as_seen_sync(user_id, conversation_id)

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def get_conversation_name(user, conversation):
    if conversation.name:
        return conversation.name

    try:
        overlords = User.objects.get(id=USER_ID_OVERLORDS)
        other_member = conversation.members.exclude(Q(user=user) | Q(user=overlords)).first()
        if other_member and other_member.user.username:
            return other_member.user.username
    except Exception:
        pass

    # Fallback to "Top Secret"
    return _("top secret")

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
def generate_template_msg(message):
    message = message[2:-2]
    parts = message.split(',')
    cmd_type = parts[0]
    params = parts[1:]

    message_templates = {
        "G": _("Game with ID {gameid} has been created."),
        "GL": _("Local game with ID {gameid} has been created."),
        "FS": _("User @{requester} has sent a friend request to @{requestee}."),
        "FA": _("User @{requester} has accepted the friend request from @{requestee}."),
        "FC": _("User @{requester} has canceled the friend request to @{requestee}."),
        "FR": _("User @{requester} has rejected the friend request from @{requestee}."),
        "FU": _("User @{requester} has removed @{requestee} from their friends list."),
        "B": _("User @{requester} has blocked @{requestee}."),
        "U": _("User @{requester} has unblocked @{requestee}."),
        "S": _("User @{requester} has started a conversation with @{requestee}."),
    }

    if cmd_type in message_templates:
        if cmd_type in ["G", "GL"]:
            return message_templates[cmd_type].format(gameid=params[0])
        else:
            return message_templates[cmd_type].format(requester=params[0], requestee=params[1])

    return _("Unknown command.")
