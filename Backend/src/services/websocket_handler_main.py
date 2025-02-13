# TODO: REMOVE WHEN FINISHED #284
# Basics
import logging, json
# Python stuff
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
# Chat stuff
from chat.utils_ws import get_other_user_async, validate_conversation_membership_async
from services.send_ws_msg import send_ws_chat_temporary, send_ws_info_msg, send_ws_badge, send_ws_badge_all, send_ws_chat, send_ws_error_msg
from chat.parse_incoming_message import check_if_msg_is_cmd, check_if_msg_contains_username
from chat.message_utils import create_msg_db, mark_all_messages_as_seen_async
from chat.models import Conversation
# Services
from asgiref.sync import sync_to_async

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

    @staticmethod
    async def handle_chat(consumer, user, message):
        from services.websocket_handler_main import check_message_keys
        from user.utils_relationship import is_blocked
        message = await sync_to_async(check_message_keys)(message, mandatory_keys=['conversationId', 'content'])
        conversation_id = message.get('conversationId')
        # Check if user is a member of the conversation
        await validate_conversation_membership_async(user, conversation_id)
        conversation = await sync_to_async(Conversation.objects.get)(id=conversation_id)
        content = message.get('content', '').strip()
        content = message.strip('*') # Messages are not allowed to start or end with a "*" because it's used for template messages
        other_user = await get_other_user_async(user, conversation_id)
        # Content can't be empty
        if not content:
            await send_ws_chat_temporary(user.id, conversation_id, _("Message content cannot be empty"))
            return
        # Check if content starts with a "/"
        # This means that the message was a command and therefore was handled
        if await check_if_msg_is_cmd(user, other_user, content):
            return
        # Check if user is blocked by other member
        if await sync_to_async(is_blocked)(user, other_user):
            await send_ws_chat_temporary(user.id, conversation_id, _("You have been blocked by this user"))
            return
        # Check if the message contains an @username
        content = await check_if_msg_contains_username(content)
        # Do db operations
        message_object = await sync_to_async(create_msg_db)(user, conversation, content)
        # Send update badge count of other user
        await send_ws_badge(other_user.id, conversation_id)
        await send_ws_badge_all(other_user.id)
        # Send the message to the channel
        await send_ws_chat(message_object)

    @staticmethod
    async def handle_seen(consumer, user, message):
        from services.websocket_handler_main import check_message_keys
        message = check_message_keys(message, mandatory_keys=['conversationId'])
        conversation_id = message.get('conversationId')
        await validate_conversation_membership_async(user, conversation_id)
        await mark_all_messages_as_seen_async(user.id, conversation_id)

def check_message_keys(text: str, mandatory_keys: list[str] = None) -> dict:
    """
    For all incoming messages we should use this function to parse the message
    therefore we can validate if the message has all the required fields
    and if not, raise an exception
    """
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
