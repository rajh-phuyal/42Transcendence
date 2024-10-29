import json
from .models import Message, Conversation
from asgiref.sync import sync_to_async  # Needed to run ORM queries in async functions
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
import logging

class ChatConsumer(AsyncWebsocketConsumer):
    

	# TODO:
    # Here it should look smth like:
    # ../servies/websocket_servcie recive msh

    # Main function to connect to the WebSocket
    # TODO: ALl the connection logic should be moved to the websocket_service
    async def connect(self):
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
        else:
            # Get the conversations the user is part of asynchronously
            user_conversations = await self.get_user_conversations(self.scope['user'])

            # Loop over the conversations asynchronously
            for conversation in await sync_to_async(list)(user_conversations):
                await self.channel_layer.group_add(
                    f'chat_{conversation.id}',  # Add the user to each conversation's WebSocket group
                    self.channel_name
                )
                print(f"User {self.scope['user'].username} added to chat_{conversation.id}")
        
            await self.accept()

    # Main function to disconnect from the WebSocket
    async def disconnect(self, close_code):
        # Remove the user from all conversation groups they were part of
        user_conversations = await self.get_user_conversations(self.scope['user'])
        for conversation in user_conversations:
            await self.channel_layer.group_discard(f'chat_{conversation.id}', self.channel_name)
        
        await self.channel_layer.group_discard(
            'global_notifications',
            self.channel_name
        )

    # Main function to receive messages from the WebSocket
    # Checks the event_type and calls the appropriate function
    #  - chat_message         = receive a chat message to store
    #  - load_conversation     = load previous messages for a conversation
    #  - notification         = handle notifications #TODO: what notiffications does the frontend send?
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

        # Broadcast the message ID to all users in this conversation
        await self.channel_layer.group_send(
            f'chat_{conversation_id}',  # Group for conversation
            {
                'type': 'chat_message',
                'message_id': message.id,  # Pass the message ID
                'conversation_id': conversation_id
            }
        )

    async def chat_message(self, event):
        message_id = event['message_id']
    
        # Fetch the message from the DB to match the correct format
        message = await sync_to_async(Message.objects.get)(id=message_id)
    
        # Fetch the user asynchronously
        sender_user = await sync_to_async(lambda: message.user.id)()
        
        # Send the message to the WebSocket client in the same format as previous messages
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': message.id,
            'sender': sender_user,  # Sender's user ID
            'content': message.content,
            'created_at': message.created_at.isoformat(),  # Add timestamp
            'conversation_id': message.conversation_id  # Include conversation ID
        }))

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
    
    # Get the conversations the user is part of
    @sync_to_async
    def get_user_conversations(self, user):
        # Query ConversationMember to get the conversations the user is part of
        logging.info(f"Getting conversations for user: {user}")
        return Conversation.objects.filter(members__user=user)
