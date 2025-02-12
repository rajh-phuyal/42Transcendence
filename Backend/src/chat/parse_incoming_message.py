# Basics
import logging, re
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
            # TODO: Implement this
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
            raise BarelyAnException(_("Invalid conversation command"))
        logging.info("Command found and executed: %s", content)
        return True
    return False

# - find all '@' in message
#    - check if the user exists
#        if exists: replace username with userid
#          -> so we can get the id when sending it to the fe and format it as @<username>@<userid>@
#          -> this ensures, that the username<->userid mapping is done only by delivery
#          -> so if a user changes the username the @<username> will update to new username - we are so smart ;)
#        if username does not exist: ignore
# - Patterns for game and tournament will be done by fe
async def check_if_msg_contains_username(message):
    if "@" in message:
        logging.info("Message contains @ expecting username(s). Full message: %s", message)
        parts = message.split("@")
        for i in range(1, len(parts)):
            allowed_chars_pattern = r'^[a-zA-Z0-9_-]+' # Username can only contain letters, numbers, underscores and hyphens
            match = re.match(allowed_chars_pattern, parts[i])
            if match:
                username = match.group()
                try:
                    user = await sync_to_async(User.objects.get)(username=username)
                    # So here we replace the username by the userid
                    # So in Case the user changes the username the message will be updated
                    # The MessageSerializer will then format the message to @<username>@<userid>@
                    message = message.replace(f"@{username}", f"@{user.id}")
                except User.DoesNotExist:
                    logging.info("Username not found: %s", username)
    return message