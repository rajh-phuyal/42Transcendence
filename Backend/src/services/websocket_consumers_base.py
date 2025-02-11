# Basics
import logging, asyncio, random, json
# Python stuff
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from copy import deepcopy
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_ws_exceptions
# Game stuff
from game.constants import GAME_FPS, GAME_STATE, GAME_PLAYER_INPUT, PADDLE_OFFSET
from game.models import Game
from game.utils import is_left_player, get_game_data, set_game_data, get_user_of_game
from game.utils_ws import update_game_state, update_game_points, send_update_game_data_msg, send_update_players_ready_msg
from game.game_physics import activate_power_ups, move_paddle, move_ball, apply_wall_bonce, check_paddle_bounce, check_if_game_is_finished, apply_point
# Services
from services.constants import PRE_USER_CHANNEL
from Backend.src.services.websocket_handler_main import WebSocketMessageHandlersMain, WebSocketMessageHandlersGame, check_message_keys
from services.chat_service import send_total_unread_counter
from services.channel_groups import update_client_in_all_conversation_groups, update_client_in_all_tournament_groups
# Channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

# Basic Connect an Disconnet functions for the WebSockets
class CustomWebSocketLogic(AsyncWebsocketConsumer):

    # Don't add a decorator here, it will be added in the child classes
    async def connect(self):
        logging.info("Opening WebSocket connection...")
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        else:
            logging.info("...for user: %s", self.scope['user'])
            return True

    # Don't add a decorator here, it will be added in the child classes
    async def disconnect(self, close_code):
        logging.info("Closing WebSocket connection...")
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        else:
            logging.info("...for user: %s", self.scope['user'])

    # Don't add a decorator here, it will be added in the child classes
    async def receive(self, text_data):
        # Check again if authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        # Parse the message (only the messageType is required at this point)
        self.message_type = check_message_keys(text_data, mandatory_keys=['messageType']).get('messageType')
