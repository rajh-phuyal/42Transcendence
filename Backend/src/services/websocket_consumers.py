from asgiref.sync import sync_to_async  # Needed to run ORM queries in async functions
import json
from django.utils import timezone
from chat.models import Message, Conversation
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser #TODO: delete later!
import logging
from django.core.cache import cache
from user.models import User
from chat.utils_ws import recieve_message
from core.decorators import barely_handle_exceptions
from django.utils.translation import gettext as _
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_ws_exceptions
from services.chat_service import setup_all_conversations

# Basic Connect an Disconnet functions for the WebSockets
class CustomWebSocketLogic(AsyncWebsocketConsumer):
    async def connect(self):
        logging.info("Opening WebSocket connection...")
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
        else:
            logging.info("...for user: %s", self.scope['user'].username)
            user_id = self.scope['user'].id
            #TODO:  Set the user's online status in cache
            cache.set(f'user_online_{user_id}', True, timeout=3000) # 3000 seconds = 50 minutes        

    async def disconnect(self, close_code):
        logging.info("Closing WebSocket connection...")
        logging.info(f"Disconnecting user: {self.scope['user'].username}")

        # Get user
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
        else:
            user = self.scope['user']
            # Set the last login time for the user
            await sync_to_async(user.update_last_seen)()
            # Remove the user's online status from cache
            cache.delete(f'user_online_{user.id}')
            logging.info(f"User {user.username} marked as offline.")
            ...

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Check again if authenitcated
        if not self.scope['user'].is_authenticated:
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        text_data_json = json.loads(text_data)
        self.message_type = text_data_json.get('messageType')
        if not self.message_type:
            raise BarelyAnException(_("Invalid websocket message format. The key 'messageType' is required."))
        logging.info(f"Received Websocket Message type: {self.message_type}")
    
    def update_user_last_seen(self, user):
        user.last_seen = timezone.now()
        user.save(update_fields=['last_seen'])

# Manages the WebSocket connection for all pages after login
class MainConsumer(CustomWebSocketLogic):
    async def connect(self):
        # Stuff from the parent class
        # ---------------------------
        await super().connect()

        # Stuff from the child class
        # ---------------------------
        
        # Add the user to all their conversation groups
        await setup_all_conversations(self.scope['user'], self.channel_name)

        # Accept the connection
        # ---------------------------
        await self.accept()

    #@barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Settign the user
        user = self.scope['user']
        if self.message_type == 'chat':
            await recieve_message(self, user, text_data)
        elif self.message_type == 'relationship':
            logging.info("Received relationship message - TODO: implement")
        # TODO: the lines below should go to: GameConsumer
        elif self.message_type == 'tournament':
            logging.info("Received tournament message - TODO: implement")
        else:
            raise BarelyAnException(_("Invalid websocket message format. The value {message_type} is not a valid message type.").format(message_type=self.message_type))

# Manages the temporary WebSocket connection for a single game
class GameConsumer(CustomWebSocketLogic):
    async def connect(self):
        # Stuff from the parent class
        # ---------------------------
        await super().connect()

        # Stuff from the child class
        # ---------------------------
        ...

        # Accept the connection
        # ---------------------------
        await self.accept()

    #@barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Settign the user
        user = self.scope['user']
        if self.message_type == 'game':
            ...
        else:
            raise BarelyAnException(_("Invalid websocket message format. The value {message_type} is not a valid message type.").format(message_type=self.message_type))

############################################################################################################
# TODO:
# BELOW IS OLD AND NEEDS TO BE SPLIT IN THE STRUCURE ABOVE
############################################################################################################
#class ChatConsumer(AsyncWebsocketConsumer):
#    # TODO:
#    # Here it should look smth like:
#    # ../servies/websocket_servcie recive msh
#
#
#    # Main function to receive messages from the WebSocket
#    # Checks the event_type and calls the appropriate function
#    #  - chat_message         = receive a chat message to store
#    #  - load_conversation     = load previous messages for a conversation
#    #  - notification         = handle notifications #TODO: what notiffications does the frontend send?
#    async def receive(self, text_data):
#        text_data_json = json.loads(text_data)
#        event_type = text_data_json.get('type', '')
#        logging.info(f"Received event: {text_data_json}")
#
#        if event_type == 'chat_message':
#            # Send the message to the group and save it
#            await self.handle_chat_message(text_data_json)
#
#        elif event_type == 'load_conversation':
#            # Load all previous messages for a conversation #TODO: dynamic loading
#            messages = await self.handle_load_conversation(text_data_json['conversation_id'])
#            await self.send(text_data=json.dumps({
#                'type': 'chat_messages',    # **Ensure you are sending the correct 'type' to the frontend**
#                'messages': messages
#            }))
#
#        elif event_type == 'notification':
#            # Handle notifications, extend later as needed
#            await self.handle_notification(text_data_json)
#        else:
#            logging.error(f"Unknown event type: {event_type}")
#
#    # Here we receive the chat message and need to process it
#    async def handle_chat_message(self, event):
#        logging.info(f"Received chat message: {event}")
#        conversation_id = event['conversation_id']
#        content = event['message']
#        
#        # Access the authenticated user from scope
#        sender = self.scope['user']
#        logging.info(f'Params: {conversation_id}, {content}, {sender}')
#        
#        if not conversation_id or not content:
#            logging.error("Missing conversation_id or message content.")
#            return  # TODO:  could also send an error back via WebSocket if desired
#        
#
#        logging.info('Params: %s, %s, %s', conversation_id, content, sender)
#
#        # Save the message in the DB
#        message = await self.save_message(conversation_id, sender, content)
#
#        # Broadcast the message ID to all users in this conversation
#        await self.channel_layer.group_send(
#            f'chat_{conversation_id}',  # Group for conversation
#            {
#                'type': 'chat_message',
#                'message_id': message.id,  # Pass the message ID
#                'conversation_id': conversation_id
#            }
#        )
#
#    async def chat_message(self, event):
#        message_id = event['message_id']
#    
#        # Fetch the message from the DB to match the correct format
#        message = await sync_to_async(Message.objects.get)(id=message_id)
#    
#        # Fetch the user asynchronously
#        sender_user = await sync_to_async(lambda: message.user.id)()
#        
#        # Send the message to the WebSocket client in the same format as previous messages
#        await self.send(text_data=json.dumps({
#            'type': 'chat_message',
#            'id': message.id,
#            'sender': sender_user,  # Sender's user ID
#            'content': message.content,
#            'created_at': message.created_at.isoformat(),  # Add timestamp
#            'conversation_id': message.conversation_id  # Include conversation ID
#        }))
#
#    @sync_to_async
#    def save_message(self, conversation_id, sender, content):
#        conversation = Conversation.objects.get(id=conversation_id)
#        return Message.objects.create(conversation=conversation, user=sender, content=content)
#
#    @sync_to_async
#    # Get all messages for the selected conversation
#    def handle_load_conversation(self, conversation_id):
#        logging.info(f"Loading conversation: {conversation_id}")
#        messages = Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
#        return [{'id': msg.id, 'sender': msg.user_id, 'content': msg.content, 'created_at': msg.created_at.isoformat()} for msg in messages]
#
#    # Example of handling notifications
#    async def handle_notification(self, event):
#        logging.info(f"Received notification: {event}")
#        # TODO: Handle notifications as needed
#    
#    # Get the conversations the user is part of
#    @sync_to_async
#    def get_user_conversations(self, user):
#        # Query ConversationMember to get the conversations the user is part of
#        logging.info(f"Getting conversations for user: {user}")
#        return Conversation.objects.filter(members__user=user)
