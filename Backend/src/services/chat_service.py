from chat.models import Message, Conversation
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from user.models import User
from chat.models import ConversationMember
import logging

User = get_user_model()

channel_layer = get_channel_layer()

def add_to_group(group_name, channel_name):
    """Add a WebSocket connection to a group"""
    async_to_sync(channel_layer.group_add)(group_name, channel_name)

def remove_from_group(group_name, channel_name):
    """Remove a WebSocket connection from a group"""
    async_to_sync(channel_layer.group_discard)(group_name, channel_name)

@sync_to_async
def setup_all_conversations(user, channel_name):
    """Add user to all conversation groups"""
    logging.info("Setting up all conversations for user: %s with channel_name: %s", user, channel_name)
    # Get all conversation IDs where the user is a member
    conversation_memberships = ConversationMember.objects.filter(user=user)
    
    for membership in conversation_memberships:
        group_name = str(membership.conversation.id)
        add_to_group(group_name, channel_name)
        logging.info(f"\tAdded user {user} to group {group_name}")


async def broadcast_message(message):
    """Broadcast a message to a conversation group"""
    group_name = str(message.conversation.id)
    logging.info(f"Broadcasting to group {group_name} from user {message.user}: {message.content}")
    await channel_layer.group_send(
        group_name,
        {
            "type:": "chat",
            "messageType": "chat",
            "conversationId": message.conversation.id,
            "messageId": message.id,
            "userId": message.user.id,
            "username": message.user.username,
            "avatar": message.user.avatar_path,
            "content": message.content,
            "createdAt": message.created_at,
            "seenAt": message.seen_at
        },
    )

#@sync_to_async
#def save_message(conversation_id, sender_id, content):
#    conversation = Conversation.objects.get(id=conversation_id)
#    sender = User.objects.get(id=sender_id)
#    return Message.objects.create(conversation=conversation, user=sender, content=content)
#
#@sync_to_async
#def get_conversation_messages(conversation_id):
#    return list(
#        Message.objects.filter(conversation_id=conversation_id).order_by("created_at").values(
#            "id", "user_id", "content", "created_at"
#        )
#    )
#