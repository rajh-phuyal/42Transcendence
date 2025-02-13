# Basics
import logging
# Django
from django.utils.translation import gettext as _
from django.contrib.auth.models import AnonymousUser
# Core
from core.exceptions import BarelyAnException
# Channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Services
from services.websocket_handler_main import check_message_keys

# Basic Connect an Disconnet functions for the WebSockets
class CustomWebSocketLogic(AsyncWebsocketConsumer):
    # Don't add a decorator here, it will be added in the child classes
    async def connect(self):
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("CustomWebSocketLogic: Opening WebSocket connection: User is not authenticated.")
            await self.close()
            self.user_id = 0
            raise BarelyAnException(_("User is not authenticated."))
        else:
            logging.info("CustomWebSocketLogic: Opening WebSocket connection: for user: %s", self.scope['user'])
            self.user_id = self.scope['user'].id
            return True

    # Don't add a decorator here, it will be added in the child classes
    async def disconnect(self, close_code):
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("CustomWebSocketLogic: Opening WebSocket connection: User is not authenticated.")
            await self.close()
            self.user_id = 0
            raise BarelyAnException(_("User is not authenticated."))
        else:
            self.user_id = self.scope['user'].id
            logging.info("CustomWebSocketLogic: Opening WebSocket connection: for user: %s", self.scope['user'])

    # Don't add a decorator here, it will be added in the child classes
    async def receive(self, text_data):
        # Check again if authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            self.user_id = 0
            raise BarelyAnException(_("User is not authenticated."))
        # Parse the message (only the messageType is required at this point)
        self.user_id = self.scope['user'].id
        self.message_type = check_message_keys(text_data, mandatory_keys=['messageType']).get('messageType')
