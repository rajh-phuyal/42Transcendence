# Basics
import logging
# Django
from django.utils.translation import gettext as _
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
        message = check_message_keys(message) # TODO: @Rajh implement deep json thing UPDATE:02.02.25 bot sure if still needed...
        if consumer.local_game or consumer.isLeftPlayer:
            set_player_input(consumer.game_id, 'playerLeft', message.get("playerLeft"))
        if consumer.local_game or not consumer.isLeftPlayer:
            set_player_input(consumer.game_id, 'playerRight', message.get("playerRight"))
