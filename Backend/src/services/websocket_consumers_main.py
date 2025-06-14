# Basics
import logging, json
# Django
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async
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
    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        # Setting the user's online status in cache
        await sync_to_async(self.user.set_online_status)(True, self.channel_name)
        # Add the user to all their conversation groups
        await update_client_in_all_conversation_groups(self.user, True)
        # Add the user to all their toruanemnt groups
        await update_client_in_all_tournament_groups(self.user, True)
        # Accept the connection
        await self.accept()
        # Send the inizial badge nummer
        await send_ws_badge_all(self.user.id)

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Remove the user's online status from cache
        await sync_to_async(self.user.set_online_status)(False)
        # Remove the user from all their conversation groups
        await update_client_in_all_conversation_groups(self.user, False)
        # Remove the user from all their toruanemnt groups
        await update_client_in_all_tournament_groups(self.user, False)
        logging.info(f"User {self.user.username} marked as offline.")

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Process the message
        await WebSocketMessageHandlersMain()[f"{self.message_type}"](self, text_data)

    # BASIC MESSAGES #

    async def info(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def error(self, event):
        await self.send(text_data=json.dumps({**event}))

    # FOR CHAT #
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def update_badge(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def new_conversation(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def typing(self, event):
        await self.send(text_data=json.dumps({**event}))

    # FOR PROFILE #
    async def reload_profile(self, event):
        await self.send(text_data=json.dumps({**event}))

    # FOR TOURNAMENT #
    async def client_role(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_info(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_member(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_members(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_game(self, event):
        await self.send(text_data=json.dumps({**event}))
