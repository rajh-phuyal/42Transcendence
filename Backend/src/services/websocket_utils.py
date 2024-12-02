import logging, json

async def send_response_message(client_consumer, type, message):
    """Send a message to a WebSocket connection."""
    logging.info(f"Sending message to connection {client_consumer}: {message}")
    message_dict = {
        "messageType": type,
        "message": message
    }
    json_message = json.dumps(message_dict)
    await client_consumer.send(text_data=json_message)