from django.db import transaction
from rest_framework.permissions import AllowAny  # Import AllowAny #TODO: remove line
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import HttpResponse #For basic ShowChatView test
from user.models import User
from .models import Conversation, ConversationMember, Message
from .serializers import ConversationSerializer, ConversationMemberSerializer, MessageSerializer
from django.shortcuts import render #TODO: remove - this is for the test chat page

class LoadUnreadMessagesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
	# TODO: return the unread messages as a single int like:
    #			{"unread":4}

class LoadConversationsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user from the request
        user = request.user

        # Get all conversations where the user is a member
        conversation_memberships = ConversationMember.objects.filter(user=user)
        conversations = [membership.conversation for membership in conversation_memberships]

        # Serialize only the conversation id and name
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class LoadConversationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, conversation_id=None):
        # Get the user from the request
        user = request.user

		# Get offset from the request for pagination
        offset = request.GET.get('offset', 0)
        
        # Validate that the conversation exists
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the sender is a member of the conversation
        if not conversation.members.filter(user=user).exists():
            return Response({'error': 'You are not a member of this conversation'}, status=status.HTTP_403_FORBIDDEN)

        # Get the last 10 messages from the conversation, ordered by creation time
        messages = Message.objects.filter(conversation=conversation).order_by('created_at')[:10]

        # TODO:
		# change from get to put since we need to update the seen_at value here!

		# Serialize the messages
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


################################################################################
# BELOW IS OLD CODE!!!
################################################################################

# TODO: remove - this is for the test chat page
def test_chat(request):
    return render(request, 'chat/test-chat.html')

class ListConversationsView(APIView):
    #authentication_classes = [JWTAuthentication]  # This tells Django to use JWT authentication
    #permission_classes = [IsAuthenticated]  # This tells Django to require authentication to access this view
    permission_classes = [AllowAny] #TODO: implement the token-based authentication!
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get all conversations where the user is a member
        conversation_memberships = ConversationMember.objects.filter(user=user)
        conversations = [membership.conversation for membership in conversation_memberships]
        
        # Serialize only the conversation id and name
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

# Create a conversation and add members
# If conversation already exists, return the conversation_id
class CreateConversationView(APIView):
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
        
        # Check if a conversation between these two users already exists
        # TODO: SHOULD BE FINE FOR NOW, BUT NEEDS TO BE FIXED IF WE INTRODUCE GROUP CHATS
        # Get the conversation IDs where the sender is a member
        sender_conversations = ConversationMember.objects.filter(user=sender).values_list('conversation_id', flat=True)

        # Check if the receiver is in any of the same conversations # TODO: wich isn't a group chat
        existing_conversation = ConversationMember.objects.filter(user=receiver, conversation__in=sender_conversations).first()

        # If the conversation exists, return the conversation information
        if existing_conversation:
            conversation = existing_conversation.conversation  # Get the conversation object from the ConversationMember instance
            return Response({'conversation_id': conversation.id, 'name': conversation.name}, status=status.HTTP_200_OK)
        
        # Start a transaction to make sure all database operations happen together
        try:
            with transaction.atomic():
                # Create the Conversation
                conversation_name = f'{sender.username} blasphemes with {receiver.username}'
                conversation_serializer = ConversationSerializer(data={'name': conversation_name})

                if conversation_serializer.is_valid():
                    conversation = conversation_serializer.save()  # Conversation is created
                else:
                    return Response(conversation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Add sender and receiver to the ConversationMember table
                conversation_member_serializer_sender = ConversationMemberSerializer(data={'conversation': conversation.id, 'user': sender.id})
                if conversation_member_serializer_sender.is_valid():
                    conversation_member_serializer_sender.save()
                else:
                    raise Exception('Error adding sender to conversation members')

                conversation_member_serializer_receiver = ConversationMemberSerializer(data={'conversation': conversation.id, 'user': receiver.id})
                if conversation_member_serializer_receiver.is_valid():
                    conversation_member_serializer_receiver.save()
                else:
                    raise Exception('Error adding receiver to conversation members')

            # If everything is successful, return a success response
            return Response({'conversation_id': conversation.id, 'name': conversation.name}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # If any error occurs during the transaction, rollback and return an error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RenameConversationView(APIView):
    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!

    def post(self, request):

        conversation_id = request.data.get('conversation_id')
        # Try to get the conversation object
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the new name from the request data
        new_name = request.data.get('new_name')

        # Perform a simple validation to check if the name is empty
        if not new_name or not new_name.strip():
            return Response({'error': 'New conversation name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        # If valid, update the conversation name
        conversation.name = new_name
        conversation.save()

        return Response({'conversation_id': conversation.id, 'new_name': conversation.name}, status=status.HTTP_200_OK)

# Send a message
class SendMessageView(APIView):
    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!
    
    def post(self, request):
        from user.models import User
        sender_id = request.data.get('sender_id')
        conversation_id = request.data.get('conversation_id')
        content = request.data.get('content')

        # Check if the sender exists
        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return Response({'error': f'Invalid sender id: {sender_id}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the conversation exists
        try:
            conversation = Chat.objects.get(id=conversation_id)
        except Chat.DoesNotExist:
            return Response({'error': f'Invalid conversation id: {conversation_id}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the sender is a member of the conversation
        try:
            ConversationMember.objects.get(conversation=conversation, user=sender)
        except ConversationMember.DoesNotExist:
            return Response({'error': 'Sender is not a member of the conversation'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the content is empty
        if not content or not content.strip():
            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
                            
        # Create the message
        message = MessageSerializer(data={'sender': sender.id, 'conversation': conversation.id, 'content': content})
        if message.is_valid():
            message = message.save()
        else:
            return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message_id': message.id, 'content': message.content}, status=status.HTTP_201_CREATED)

class ShowConversationView(APIView):
    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!

    def post(self, request):
        

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
                    <h3>Last 10 Messages in Chat (id:{conversation.id}):</h3>
                    <h2>»{conversation.name}« </h2>
                    <ul style="list-style-type: none; padding: 0;">
        """

        # Loop over the messages and format them
        for message in messages:
            # Format the timestamp
            formatted_time = message.created_at.strftime('%Y-%m-%d %H:%M:%S')

            # Check if the message was sent by the current sender
            if message.user.id == sender_id:
                alignment = "message-right"
            else:
                alignment = "message-left"

            # Add each message to the HTML with conditional alignment
            html_content += f"""
                <li class="message {alignment}">
                    <strong>{message.user.username}:</strong> {message.content}
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
