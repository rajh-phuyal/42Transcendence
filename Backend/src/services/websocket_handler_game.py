# Basics
import logging, json

# Python stuff
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async

# Game stuff
from game.models import Game
from game.utils_ws import init_game, update_game_state

# Chat stuff
from chat.utils_ws import process_incoming_chat_message, process_incoming_seen_message

# Services
from services.chat_service import broadcast_chat_message

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
    async def handle_game(consumer, user, message):
        ...
        logging.info(f"Hanlding game message: {message}. tbd!")

    @staticmethod
    async def handle_playerInput(consumer, user, message):
        message = check_message_keys(message) # TODO: @Rajh implement deep json thing UPDATE:02.02.25 bot sure if still needed...
        if consumer.local_game or consumer.isLeftPlayer:
            cache.set(f'game_{consumer.game_id}_playerLeft', message.get("playerLeft"), timeout=3000)
        if consumer.local_game or not consumer.isLeftPlayer:
            cache.set(f'game_{consumer.game_id}_playerRight', message.get("playerRight"), timeout=3000)
