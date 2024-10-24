import json
from .models import Message, Conversation
from asgiref.sync import sync_to_async  # Needed to run ORM queries in async functions
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
import logging

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        # In this example, we're connecting to a global notification channel for now
        await self.channel_layer.group_add(
            'global_notifications',  # Single WebSocket group for notifications
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'global_notifications',
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse the incoming WebSocket message
        logging.info(f"Received message: {text_data}")
        text_data_json = json.loads(text_data)
        event_type = text_data_json.get('type', '')

        # Handle different event types
        if event_type == 'chat_message':
            # Handle chat messages
            await self.handle_chat_message(text_data_json)
        elif event_type == 'load_messages':
            # Handle loading messages for a conversation
            messages = await self.get_messages(text_data_json['conversation_id'])
            await self.send(text_data=json.dumps({
                'type': 'chat_messages',
                'messages': messages
            }))
#        elif event_type == 'friend_request':
#            # Handle friend requests
#            # TODO: this could come in handy later for the notification system
        elif event_type == 'notification':
            # Handle other notifications (you can extend this as needed)
            await self.handle_notification(text_data_json)

    # Example of handling a chat message
    async def handle_chat_message(self, event):
        logging.info(f"Sending message: {event['message']} from user: {self.user.id}")
        # You can do any message processing here
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': self.user.id
        }))
    
    @sync_to_async
    def get_messages(self, conversation_id):
        # Get all messages for the selected conversation
        messages = Message.objects.filter(conversation_id=conversation_id).order_by('created_at')
        return [{'id': msg.id, 'sender': msg.user_id, 'content': msg.content, 'created_at': msg.created_at.isoformat()} for msg in messages]

    # Example of handling notifications
    async def handle_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'event': event['event'],
            'content': event['content']
        }))