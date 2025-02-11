# Basic function to send a message to a user via WebSocket
async def send_ws_msg_to_user(user_id, **message):
    channel_name =  cache.get(f'{PRE_USER_CHANNEL}{user_id}')
    if channel_name:
        channel_layer = get_channel_layer()
        # Send the message to the WebSocket connection associated with that channel name
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user_id}.")

async def send_ws_badge():
    ...

async def send_ws_badge_ws__all():
    ...

async def send_ws_chat():
    ...

# TODO: should this use the serializer?
async def send_ws_chat_temporary(user_id, conversation_id, content):
    from services.websocket_handler_main import send_message_to_user
    message = {
        "messageType": "chat",
        "type": "chat_message",
        "avatar": AVATAR_OVERLORDS,
        "content": content,
        "conversationId": conversation_id,
        "createdAt": timezone.now().isoformat(),  # TODO: Issue #193
        "messageId": 1,
        "seenAt": None,
        "userId": USER_ID_OVERLORDS,
        "username": USERNAME_OVERLORDS
    }
    await send_message_to_user(user_id, **message)

async def send_ws_other():
    ...

async def send_ws_new_conversation():
    ...

