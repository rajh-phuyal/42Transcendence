import logging, json
from django.core.cache import cache
from channels.layers import get_channel_layer

# To send by consumer
async def send_response_message(client_consumer, type, message):
    """Send a message to a WebSocket connection."""
    logging.info(f"Sending message to connection {client_consumer}: {message}")
    message_dict = {
        "messageType": type,
        "message": message
    }
    json_message = json.dumps(message_dict)
    await client_consumer.send(text_data=json_message)

# To send by user id
async def send_message_to_user(user_id, **message):
    channel_name =  cache.get(f'user_channel_{user_id}', None)
    if channel_name:
        channel_layer = get_channel_layer()
        # Send the message to the WebSocket connection associated with that channel name
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user_id}.")