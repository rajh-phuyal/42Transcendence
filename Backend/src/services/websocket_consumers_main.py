# Basics
import logging, json
# Python stuff
from django.utils.translation import gettext as _
from asgiref.sync import sync_to_async
from django.core.cache import cache
# Services
from services.constants import PRE_USER_CHANNEL
from services.websocket_handler_main import WebSocketMessageHandlersMain
from services.channel_groups import update_client_in_all_conversation_groups, update_client_in_all_tournament_groups
# Channels
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from services.websocket_consumers_base import CustomWebSocketLogic

# Manages the WebSocket connection for all pages after login
class MainConsumer(CustomWebSocketLogic):
    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    #@barely_handle_ws_exceptions TODO: unccomment
    async def connect(self):
        await super().connect()
        user = self.scope['user']
        # Setting the user's online status in cache
        user.set_online_status(True)
        # Store the WebSocket channel to the cache with the user ID as the key
        cache.set(f'{PRE_USER_CHANNEL}{user.id}', self.channel_name, timeout=3000)
        # Add the user to all their conversation groups
        await update_client_in_all_conversation_groups(user, True)
        # Add the user to all their toruanemnt groups
        await update_client_in_all_tournament_groups(user, True)
        # Accept the connection
        await self.accept()
        # Send the inizial badge nummer
        # TODO: activate this again: await send_total_unread_counter(user.id)

    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    #@barely_handle_ws_exceptions TODO: uncomment
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        user = self.scope['user']
        # Set the last login time for the user
        await sync_to_async(user.update_last_seen)()
        # Remove the user's online status from cache
        user.set_online_status(False)
        # Remove the user from all their conversation groups
        await update_client_in_all_conversation_groups(user, False)
        # Remove the user from all their toruanemnt groups
        await update_client_in_all_tournament_groups(user, False)
        # Remove the user's WebSocket channel from cache
        cache.delete(f'user_channel_{user.id}')
        logging.info(f"User {user.username} marked as offline.")

    # TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
    #@barely_handle_ws_exceptions TODO: uncomment this
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Setting the user
        user = self.scope['user']
        # Process the message
        await WebSocketMessageHandlersMain()[f"{self.message_type}"](self, user, text_data)

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

