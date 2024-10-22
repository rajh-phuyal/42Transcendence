# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework_simplejwt.tokens import AccessToken

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the JWT token from the query string
        token = self.scope['query_string'].decode().split('=')[-1]

        try:
            # Decode the JWT token to get the user ID
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            # Fetch the user object and set it in the scope
            self.scope['user'] = await self.get_user(user_id)  # You need to implement this method
        except:
            # Log errors and reject connection
            print(f"Token validation error: {e}")
            await self.close()

        # Only allow connection if the user is authenticated
        if self.scope['user'].is_authenticated:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            # Join the room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()
        else:
            # If user is not authenticated, reject the connection
            await self.close()

    async def disconnect(self, close_code):
        # Leave the room group on WebSocket disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def get_user(self, user_id):
        # Fetch user from the database (implement this according to your project)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = await User.objects.get(id=user_id)
            return user
        except User.DoesNotExist:
            return AnonymousUser()
