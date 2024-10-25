import json
from .models import Message, Conversation
from asgiref.sync import sync_to_async  # Needed to run ORM queries in async functions
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
import logging

class ChatConsumer(AsyncWebsocketConsumer):
    
	# Main function to connect to the WebSocket
    async def connect(self):
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            await self.close()
        else:
            # In this example, we're connecting to a global notification channel for now
            await self.channel_layer.group_add(
                'global_notifications',  # Single WebSocket group for notifications
                self.channel_name
            )
            await self.accept()
        

	# Main function to disconnect from the WebSocket
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'global_notifications',
            self.channel_name
        )

	# Main function to receive messages from the WebSocket
    # Checks the event_type and calls the appropriate function
    #  - chat_message 		= receive a chat message to store
    #  - load_conversation 	= load previous messages for a conversation
    #  - notification 		= handle notifications #TODO: what notiffications does the frontend send?
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type', '')
        logging.info(f"Received event: {text_data_json}")

        if event_type == 'chat_message':
            # Send the message to the group and save it
            await self.handle_chat_message(text_data_json)

        elif event_type == 'load_conversation':
            # Load all previous messages for a conversation #TODO: dynamic loading
            messages = await self.handle_load_conversation(text_data_json['conversation_id'])
            await self.send(text_data=json.dumps({
                'type': 'chat_messages',    # **Ensure you are sending the correct 'type' to the frontend**
                'messages': messages
            }))

        elif event_type == 'notification':
            # Handle notifications, extend later as needed
            await self.handle_notification(text_data_json)
        else:
            logging.error(f"Unknown event type: {event_type}")

    # Here we receive the chat message and need to process it
    async def handle_chat_message(self, event):
        logging.info(f"Received chat message: {event}")
        conversation_id = event['conversation_id']
        content = event['message']
        
		# Access the authenticated user from scope
        sender = self.scope['user']
        logging.info(f'Params: {conversation_id}, {content}, {sender}')
        
        if not conversation_id or not content:
            logging.error("Missing conversation_id or message content.")
            return  # TODO:  could also send an error back via WebSocket if desired
        

        logging.info('Params: %s, %s, %s', conversation_id, content, sender)

        # Save the message in the DB
        message = await self.save_message(conversation_id, sender, content)

        # Broadcast the message to all users in this conversation
        await self.channel_layer.group_send(
            f'chat_{conversation_id}',  # Group for conversation
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': sender.username,
                'conversation_id': conversation_id
            }
        )

    @sync_to_async
    def save_message(self, conversation_id, sender, content):
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, user=sender, content=content)

    @sync_to_async
	# Get all messages for the selected conversation
    def handle_load_conversation(self, conversation_id):
        logging.info(f"Loading conversation: {conversation_id}")
        messages = Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
        return [{'id': msg.id, 'sender': msg.user_id, 'content': msg.content, 'created_at': msg.created_at.isoformat()} for msg in messages]

    # Example of handling notifications
    async def handle_notification(self, event):
        logging.info(f"Received notification: {event}")
        # TODO: Handle notifications as needed