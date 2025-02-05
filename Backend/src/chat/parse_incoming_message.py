# Basics
import logging

# Django stuff
from django.utils import timezone
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async

# Core stuff
from core.exceptions import BarelyAnException

# User stuff
from user.constants import USER_ID_OVERLORDS, AVATAR_OVERLORDS, USERNAME_OVERLORDS
from user.models import User


# This will be called on a incoming chat message and has to do:
# - check if message starts with '/'
async def check_if_msg_is_cmd(user, other_user, conversation_id, content):
    from user.utils_relationship import block_user, unblock_user, send_request, accept_request, cancel_request, reject_request, unfriend
    if content.startswith("/"):
        content_upper = content.upper()
        logging.info("Message starts with / expecting a cmd. Full message: %s", content)
        if content_upper == "/FS":
            await sync_to_async(send_request)(user, other_user)
        elif content_upper == "/FA":
            await sync_to_async(accept_request)(user, other_user)
        elif content_upper == "/FC":
            await sync_to_async(cancel_request)(user, other_user)
        elif content_upper == "/FR":
            await sync_to_async(reject_request)(user, other_user)
        elif content_upper == "/FU":
            await sync_to_async(unfriend)(user, other_user)
        elif content_upper == "/B":
            await sync_to_async(block_user)(user, other_user)
        elif content_upper == "/U":
            await sync_to_async(unblock_user)(user, other_user)
        elif content_upper.startswith("/G,"):
            # Create a Game
            logging.info("Create a Game")
            temp = content_upper.split(",")
            localGame = False
            mapNumer = 0
            powerups = False
            #if temp.length != 4:
            #/G,normal,ufo,true
            #/G,local,ufo,true
            #await sync_to_async(create_game)(user.id, other_user.id, map_number, values["powerups"], False)
        else:
            raise BarelyAnException(_("Invalid command"))
        return True
    return False

# - find all '@' in message
#    - check if the user exists
#        if exists: replace username with userid and mark message wirth prefix **
#          -> so we can get the id when sending it to the fe and format it as @<username>@<userid>@
#          -> this ensures, that the username<->userid mapping is done only by delivery
#          -> so if a user changes the username the @<username> will update to new username - we are so smart ;)
#        if username does not exist: ignore
# - Patterns for game and tournament will be done by fe
async def check_if_msg_contains_username(user, other_user, conversation_id, content):
    if "@" in content:
        logging.info("Message contains @ expecting username(s). Full message: %s", content)


# This functions allows us to send a message to the user which won't persist
# in the database and therfore is gone after the user reloads the page
async def send_temporary_info_msg(user_id, conversation_id, content):
    from services.websocket_utils import send_response_message
    message = {
        "avatar": AVATAR_OVERLORDS,
        "content": content,
        "conversationId": conversation_id,
        "createdAt": timezone.now(),  # TODO: Issue #193
        "messageId": 1,
        "messageType": "chat",
        "seenAt": None,
        "type": "message",
        "userId": USER_ID_OVERLORDS,
        "username": USERNAME_OVERLORDS
    }
    await send_response_message(user_id, conversation_id, **message)