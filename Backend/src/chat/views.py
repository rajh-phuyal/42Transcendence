from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, ChatMember, Message
from .serializers import ChatSerializer, ChatMemberSerializer, MessageSerializer
from django.users.models import User

# Create a chat and add members
class CreateChatView(APIView):
    def post(self, request):
        user1 = request.data.get('user1')
        user2 = request.data.get('user2')

        # Create the chat
        chat_name = f'{user1} and {user2} conversation'
        chat = Chat.objects.create(name=chat_name, is_group_chat=False)

        # Add both users to the chat
        ChatMember.objects.create(chat=chat, user_id=user1)
        ChatMember.objects.create(chat=chat, user_id=user2)

        return Response({'chat_id': chat.id, 'name': chat.name}, status=status.HTTP_201_CREATED)

# Send a message
class SendMessageView(APIView):
    def post(self, request, chat_id):
        sender_id = request.data.get('sender_id')
        content = request.data.get('content')

        # Create the message
        message = Message.objects.create(
            chat_id=chat_id,
            sender_id=sender_id,
            content=content
        )

        return Response({'message_id': message.id, 'content': message.content}, status=status.HTTP_201_CREATED)
