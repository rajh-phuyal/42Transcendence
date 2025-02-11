# Basics
import logging, json

# Python stuff
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException

# Chat stuff
from chat.utils_ws import process_incoming_chat_message, process_incoming_seen_message

# Services

## HANDLER FOR MAIN WEBSOCKET CONNECTION
## ------------------------------------------------------------------------------------------------
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

    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    @staticmethod
    async def handle_chat(consumer, user, message):
        await process_incoming_chat_message(consumer, user, message)
        logging.info(f"Parsed backend object: {message}")

    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    @staticmethod
    async def handle_seen(consumer, user, message):
        logging.info("Received seen message")
        await process_incoming_seen_message(consumer, user, message)

    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    @staticmethod
    async def handle_relationship(consumer, user, message):
        logging.info("Received relationship message - TODO: issue #206 implement")

# For all incoming messages we should use this function to parse the message
# therefore we can validate if the message has all the required fields
# and if not, raise an exception
# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
def check_message_keys(text: str, mandatory_keys: list[str] = None) -> dict:
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
