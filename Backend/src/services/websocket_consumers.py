from asgiref.sync import sync_to_async
import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
import logging
from django.core.cache import cache
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_ws_exceptions
from services.chat_service import setup_all_conversations, send_total_unread_counter
from services.websocket_utils import WebSocketMessageHandlersMain, WebSocketMessageHandlersGame, parse_message

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
        self.message_type = parse_message(text_data, mandatory_keys=['messageType']).get('messageType')
        logging.info(f"Received Websocket Message type: {self.message_type}")

    def update_user_last_seen(self, user):
        user.last_seen = timezone.now()
        user.save(update_fields=['last_seen'])

# Manages the WebSocket connection for all pages after login
class MainConsumer(CustomWebSocketLogic):
    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        # Setting the user's online status in cache
        user = self.scope['user']
        cache.set(f'user_online_{user.id}', True, timeout=3000) # 3000 seconds = 50 minutes
        # Store the WebSocket channel to the cache with the user ID as the key
        cache.set(f'user_channel_{user.id}', self.channel_name, timeout=3000)
        # Add the user to all their conversation groups
        await setup_all_conversations(user, self.channel_name, intialize=True)
        # Accept the connection
        await self.accept()
        # Send the inizial badge nummer
        await send_total_unread_counter(user.id)

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        user = self.scope['user']
        # Set the last login time for the user
        await sync_to_async(user.update_last_seen)()
        # Remove the user's online status from cache
        cache.delete(f'user_online_{user.id}')
        # Remove the user's WebSocket channel from cache
        cache.delete(f'user_channel_{user.id}')
        logging.info(f"User {user.username} marked as offline.")
        # Remove the user from all their conversation groups
        await setup_all_conversations(user, self.channel_name, intialize=False)

    @barely_handle_ws_exceptions
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

# Manages the temporary WebSocket connection for a single game
class GameConsumer(CustomWebSocketLogic):
    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        # Doing game stuff
        ...
        # Accept the connection
        await self.accept()

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Doing game stuff
        ...

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Setting the user
        user = self.scope['user']
        # Process the message
        await WebSocketMessageHandlersGame()[f"{self.message_type}"](self, user, text_data)
