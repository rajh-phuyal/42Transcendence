from django.db import transaction
from rest_framework.permissions import AllowAny  # Import AllowAny #TODO: remove line
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse #For basic ShowChatView test
from .models import Chat, ChatMember, Message
from .serializers import ChatSerializer, ChatMemberSerializer, MessageSerializer

# Create a chat and add members
# If chat already exists, return the chat_id
class CreateChatView(APIView):
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!

    def post(self, request):
        from user.models import User
        sender_id = request.data.get('sender_id')
        receiver_id = request.data.get('receiver_id')

        # Validate that sender and receiver exist
        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return Response({'error': f'Invalid sender id: {sender_id}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'error': f'Invalid receiver id: {receiver_id}'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if sender and receiver are the same
        if sender == receiver:
            return Response({'error': 'Sender and receiver cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a chat between these two users already exists
        # TODO: SHOULD BE FINE FOR NOW, BUT NEEDS TO BE FIXED IF WE INTRODUCE GROUP CHATS
        # Get the chat IDs where the sender is a member
        sender_chats = ChatMember.objects.filter(user=sender).values_list('chat_id', flat=True)

        # Check if the receiver is in any of the same chats
        existing_chat = ChatMember.objects.filter(user=receiver, chat_id__in=sender_chats).first()

        # If the chat exists, return the chat information
        if existing_chat:
            chat = existing_chat.chat  # Get the chat object from the ChatMember instance
            return Response({'chat_id': chat.id, 'name': chat.name}, status=status.HTTP_200_OK)
        
        # Start a transaction to make sure all database operations happen together
        try:
            with transaction.atomic():
                # Create the Chat
                chat_name = f'{sender.username} blasphemes with {receiver.username}'
                chat_serializer = ChatSerializer(data={'name': chat_name})

                if chat_serializer.is_valid():
                    chat = chat_serializer.save()  # Chat is created
                else:
                    return Response(chat_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Add sender and receiver to the ChatMember table
                chat_member_serializer_sender = ChatMemberSerializer(data={'chat': chat.id, 'user': sender.id})
                if chat_member_serializer_sender.is_valid():
                    chat_member_serializer_sender.save()
                else:
                    raise Exception('Error adding sender to chat members')

                chat_member_serializer_receiver = ChatMemberSerializer(data={'chat': chat.id, 'user': receiver.id})
                if chat_member_serializer_receiver.is_valid():
                    chat_member_serializer_receiver.save()
                else:
                    raise Exception('Error adding receiver to chat members')

            # If everything is successful, return a success response
            return Response({'chat_id': chat.id, 'name': chat.name}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If any error occurs during the transaction, rollback and return an error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RenameChatView(APIView):
    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!

    def post(self, request):

        chat_id = request.data.get('chat_id')
        # Try to get the chat object
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the new name from the request data
        new_name = request.data.get('new_name')

        # Perform a simple validation to check if the name is empty
        if not new_name or not new_name.strip():
            return Response({'error': 'New chat name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # If valid, update the chat name
        chat.name = new_name
        chat.save()

        return Response({'chat_id': chat.id, 'new_name': chat.name}, status=status.HTTP_200_OK)

# Send a message
class SendMessageView(APIView):
    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!
    
    def post(self, request):
        from user.models import User
        sender_id = request.data.get('sender_id')
        chat_id = request.data.get('chat_id')
        content = request.data.get('content')

        # Check if the sender exists
        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return Response({'error': f'Invalid sender id: {sender_id}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the chat exists
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': f'Invalid chat id: {chat_id}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the sender is a member of the chat
        try:
            ChatMember.objects.get(chat=chat, user=sender)
        except ChatMember.DoesNotExist:
            return Response({'error': 'Sender is not a member of the chat'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the content is empty
        if not content or not content.strip():
            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
                            
        # Create the message
        message = MessageSerializer(data={'sender': sender.id, 'chat': chat.id, 'content': content})
        if message.is_valid():
            message = message.save()
        else:
            return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message_id': message.id, 'content': message.content}, status=status.HTTP_201_CREATED)

class ShowChatView(APIView):
    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!

    def post(self, request):
        from user.models import User
        # Get sender_id and chat_id from the request
        sender_id = request.data.get('sender_id')
        chat_id = request.data.get('chat_id')

        # Validate that the sender exists
        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return Response({'error': 'Sender not found'}, status=status.HTTP_404_NOT_FOUND)

         # Validate that the chat exists
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the sender is a member of the chat
        if not chat.members.filter(user=sender).exists():
            return Response({'error': 'You are not a member of this chat'}, status=status.HTTP_403_FORBIDDEN)

        # Get the last 10 messages from the chat, ordered by creation time
        messages = Message.objects.filter(chat=chat).order_by('created_at')[:10]

         # Create a simple HTML structure to return the messages
        html_content = f"""
        <html>
            <head>
                <style>
                    .message-container {{ max-width: 600px; margin: 0 auto; padding: 10px; }}
                    .message {{ padding: 10px; margin-bottom: 10px; border-radius: 10px; max-width: 80%; }}
                    .message-left {{ text-align: left; background-color: #f1f1f1; float: left; clear: both; }}
                    .message-right {{ text-align: right; background-color: #d1e7dd; float: right; clear: both; }}
                    .timestamp {{ font-size: 0.8em; color: gray; margin-top: 5px; }}
                </style>
            </head>
            <body>
                <div class="message-container">
                    <h3>Last 10 Messages in Chat:</h3>
                    <h2>» {chat.name}« </h2>
                    <ul style="list-style-type: none; padding: 0;">
        """

        # Loop over the messages and format them
        for message in messages:
            # Format the timestamp
            formatted_time = message.created_at.strftime('%Y-%m-%d %H:%M:%S')

            # Check if the message was sent by the current sender
            if message.sender.id == sender_id:
                alignment = "message-right"
            else:
                alignment = "message-left"

            # Add each message to the HTML with conditional alignment
            html_content += f"""
                <li class="message {alignment}">
                    <strong>{message.sender.username}:</strong> {message.content}
                    <div class="timestamp">{formatted_time}</div>
                </li>
            """

        # Close the HTML content
        html_content += """
                    </ul>
                </div>
            </body>
        </html>
        """

        return HttpResponse(html_content, content_type='text/html')
