# Basics
import logging
# Django
from django.utils.translation import gettext as _
# User
from user.constants import USER_ID_AI, USER_ID_FLATMATE
# Game
from game.game_cache import set_player_input
# Services
from services.websocket_handler_main import check_message_keys

## HANDLER FOR GAME WEBSOCKET CONNECTION
## ------------------------------------------------------------------------------------------------
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
    async def handle_playerInput(consumer, message):
        message = check_message_keys(message)
        # This is kind of confusing but u need to be able to stear the left paddele if:
        # - u are the left player
        # - the left player is the flatmate
        # - it is a local game and the player is not the AI (in case of a local tournament game)
        if consumer.isLeftPlayer or consumer.leftUser.id == USER_ID_FLATMATE or (consumer.game.tournament and consumer.game.tournament.local_tournament and consumer.leftUser.id != USER_ID_AI):
            set_player_input(consumer.game_id, 'playerLeft', message.get("playerLeft"))
        if not consumer.isLeftPlayer or consumer.rightUser.id == USER_ID_FLATMATE or (consumer.game.tournament and consumer.game.tournament.local_tournament and consumer.rightUser.id != USER_ID_AI):
            set_player_input(consumer.game_id, 'playerRight', message.get("playerRight"))
