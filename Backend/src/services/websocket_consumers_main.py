# Basics
import logging, json
# Django
from django.utils.translation import gettext as _
# Core
from core.decorators import barely_handle_ws_exceptions
# Services
from services.websocket_consumers_base import CustomWebSocketLogic
from services.websocket_handler_main import WebSocketMessageHandlersMain
from services.channel_groups import update_client_in_all_conversation_groups, update_client_in_all_tournament_groups
from services.send_ws_msg import send_ws_badge_all
# Channels
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

# Manages the WebSocket connection for all pages after login
class MainConsumer(CustomWebSocketLogic):
    # TODO: remove this comment @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        # Setting the user's online status in cache
        self.user.set_online_status(True, self.channel_name)
        # Add the user to all their conversation groups
        await update_client_in_all_conversation_groups(self.user, True)
        # Add the user to all their toruanemnt groups
        await update_client_in_all_tournament_groups(self.user, True)
        # Accept the connection
        await self.accept()
        # Send the inizial badge nummer
        await send_ws_badge_all(self.user.id)

    # TODO: remove this comment @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Remove the user's online status from cache
        self.user.set_online_status(False)
        # Remove the user from all their conversation groups
        await update_client_in_all_conversation_groups(self.user, False)
        # Remove the user from all their toruanemnt groups
        await update_client_in_all_tournament_groups(self.user, False)
        logging.info(f"User {self.user.username} marked as offline.")

    # TODO: remove this comment @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Process the message
        await WebSocketMessageHandlersMain()[f"{self.message_type}"](self, text_data)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def update_badge(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def new_conversation(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_subscription(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def info(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def error(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_create(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_set_deadline(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_score(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_rank(self, event):
        await self.send(text_data=json.dumps({**event}))
