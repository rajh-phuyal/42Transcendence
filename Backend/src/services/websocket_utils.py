import logging, json
from django.core.cache import cache
from chat.utils_ws import process_incoming_chat_message, process_incoming_seen_message
from services.chat_service import broadcast_message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _

class WebSocketMessageHandlersMain:

    """If u wanna handle a new message type, add a new static method with the name handle_{message_type}"""
    def __getitem__(self, key):
        method_name = f"handle_{key}"

        # Use getattr to fetch the static method
        method = getattr(self, method_name, None)

        # If the method exists, return it, otherwise raise an error
        if callable(method):
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no method '{method_name}'")
    
    @staticmethod
    async def handle_chat(consumer, user, message):
        message = await process_incoming_chat_message(consumer, user, message)
        logging.info(f"Parsed backend object: {message}")
        await broadcast_message(message)
    
    @staticmethod
    async def handle_seen(consumer, user, message):
        logging.info("Received seen message")
        await process_incoming_seen_message(consumer, user, message)

    @staticmethod
    async def handle_relationship(consumer, user, message):
        logging.info("Received relationship message - TODO: issue #206 implement")

class WebSocketMessageHandlersGame:

    """If u wanna handle a new message type, add a new static method with the name handle_{message_type}"""
    def __getitem__(self, key):
        method_name = f"handle_{key}"

        # Use getattr to fetch the static method
        method = getattr(self, method_name, None)

        # If the method exists, return it, otherwise raise an error
        if callable(method):
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no method '{method_name}'")
    
    @staticmethod
    async def handle_game(consumer, user, message):
        ...
        logging.info(f"Hanlding game message: {message}. tbd!")

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

@async_to_sync
async def send_message_to_user_sync(user_id, **message):
    await send_message_to_user(user_id, **message)

# For all incoming messages we should use this function to parse the message
# therefore we can validate if the message has all the required fields
# and if not, raise an exception
def parse_message(text: str, mandatory_keys: list[str] = None) -> dict:
    _message = json.loads(text)

    message_type = _message.get('messageType', None)
    if not message_type:
        raise BarelyAnException(_("messageType is required"))

    if not mandatory_keys:
        return _message

    for key in mandatory_keys:
        if key not in _message:
            raise BarelyAnException(_("key '{key}' is required in message type '{message_type}'").format(key=key, message_type=message_type))

    return _message
