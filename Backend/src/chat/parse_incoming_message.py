# Basics
import logging, re
# Django
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async
# Core
from core.exceptions import BarelyAnException
# User
from user.models import User
# Game
from game.constants import MAPNAME_TO_MAPNUMBER
from game.utils import create_game

async def check_if_msg_is_cmd(user, other_user, content):
    """
    A incoming ws chat message could be also a cmd. If so this function will
    call the appropriate function to handle the cmd and return True.
    Therefore the normal message will not be send to the conversation.
    The cmd handle function e.g. 'send_request' will create a template message
    e.g. **FS,12,42**store it in the db and send it to the conversation.
    """
    from user.utils_relationship import block_user, unblock_user, send_request, accept_request, cancel_request, reject_request, unfriend
    logging.info(f"User/other_user: %s/%s", user.id, other_user.id)
    if content.startswith("/"):
        content_upper = content.upper()
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
        elif content_upper.startswith("/G"):
            # Create a Game
            # e.g: /G,UFO,REMOTE,YES
            #      /G,SNOWMAN,LOCAL,NO
            temp = content_upper.split(",")
            if len(temp) != 4:
                raise BarelyAnException(_("Invalid conversation command"))
            logging.info(f"Mapname: %s", temp[1].lower())
            map_number = MAPNAME_TO_MAPNUMBER.get(temp[1].lower(), None)
            if not map_number:
                raise BarelyAnException(_("Invalid map name"))
            if temp[2] not in ["LOCAL", "REMOTE"]:
                raise BarelyAnException(_("Invalid game type"))
            local_game = False
            if temp[2] == "local":
                local_game = True
            if temp[3] not in ["YES", "NO"]:
                raise BarelyAnException(_("Invalid powerup value"))
            powerups = False
            if temp[3] == "yes":
                powerups = True
            logging.info(f"User/Opponent: %s/%s", user.id, other_user.id)
            game_id, sucess = await sync_to_async(create_game)(user, other_user.id, map_number, powerups, local_game)
            if not sucess:
                raise BarelyAnException(_("Game already exists: #G#{id}#").format(id=game_id))
        else:
            raise BarelyAnException(_("Invalid conversation command"))
        logging.info(f"Command found and executed: %s", content)
        return True
    return False

async def check_if_msg_contains_username(message):
    """
    A incoming ws chat message could contain a username mention like @astein
    Since usernames can be changed we need to replace the username by the userid
    @astein -> @42
    The MessageSerializer will then format the message to @<username>@<userid>@
    when delivering the Message back to the frontend always with the updated username
    The frontend will then create a clickable @username hyperlink to /profile/<userid>

    NOTE: Mentioned Games and Tournaments don't need to be replaced here because:
    - Games don't have names                #G#<gameid>#
    - Tournament names can't be changed     #T#<tournamentName>#<tournamentId>#
    """
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
                    message = message.replace(f"@{username}", f"@{user.id}")
                except User.DoesNotExist:
                    logging.info("Username not found: %s", username)
    return message