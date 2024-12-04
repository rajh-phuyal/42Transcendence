from chat.models import Message, Conversation
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from user.models import User
from chat.models import ConversationMember
import logging
from services.websocket_utils import send_message_to_user
User = get_user_model()
channel_layer = get_channel_layer()

# channel_name is the WebSocket connection ID for a user
# group_name is the conversation ID
@sync_to_async
def setup_all_conversations(user, channel_name, intialize=True):
    logging.info("MODE: %d, Configuring conversations for user: %s with channel_name: %s", intialize, user, channel_name)
    # Get all conversation IDs where the user is a member
    conversation_memberships = ConversationMember.objects.filter(user=user)
    for membership in conversation_memberships:
        group_name = f"conversation_{membership.conversation.id}"
        if intialize:
            async_to_sync(channel_layer.group_add)(group_name, channel_name)
            logging.info(f"\tAdded user {user} to group {group_name}")
        else:
            async_to_sync(channel_layer.group_discard)(group_name, channel_name)
            logging.info(f"\tRemoved user {user} from group {group_name}")

async def broadcast_message(message):
    group_name = f"conversation_{message.conversation.id}"
    logging.info(f"Broadcasting to group {group_name} from user {message.user}: {message.content}")
    await channel_layer.group_send(
        group_name,
        {
            "type": "chat_message",
            "messageType": "chat",
            "conversationId": message.conversation.id,
            "messageId": message.id,
            "userId": message.user.id,
            "username": message.user.username,
            "avatar": message.user.avatar_path,
            "content": message.content,
            "createdAt": message.created_at.isoformat(),
            "seenAt": message.seen_at.isoformat() if message.seen_at else None
        }
    )

@sync_to_async
def setup_all_badges_sync(user_id):
    logging.info("Sending the initial badge count to the user: %s", user_id)
    conversation_memberships = ConversationMember.objects.filter(user=user_id)
    badges = []
    total_unseen_messages = 0
    for membership in conversation_memberships:
        logging.info(f"\t\tConversation {membership.conversation.id} has {membership.unread_counter} unseen messages")
        badges.append({
            "id": membership.conversation.id,
            "value": membership.unread_counter
        })
        total_unseen_messages += membership.unread_counter
    return badges, total_unseen_messages

async def send_badges_to_user(user_id, badges, total_unseen_messages):
    # Send badges updates
    for badge in badges:
        msg_data = {
            "type": "update_badge",
            "messageType": "updateBadge",
            "what": "conversation",
            "id": badge['id'],
            "value": badge['id']
        } 
        await send_message_to_user(user_id, **msg_data)

    # Send total unseen message count
    msg_data = {
        "type": "update_badge",
        "messageType": "updateBadge",
        "what": "all",
        "value": total_unseen_messages
    }
    await send_message_to_user(user_id, **msg_data)
    
async def setup_all_badges(user_id):
    logging.info("Setting up all badges for user: %s", user_id)

    # Step 1: Get badges and total unseen messages synchronously
    badges, total_unseen_messages = await setup_all_badges_sync(user_id)
    
    # Step 2: Send the badges data asynchronously
    await send_badges_to_user(user_id, badges, total_unseen_messages)