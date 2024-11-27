from django.db.models import Q
from core.base_views import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from chat.models import Conversation, ConversationMember, Message
from chat.serializers import ConversationSerializer, ConversationMemberSerializer, MessageSerializer
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from rest_framework import status
from django.utils import timezone
from .utils import mark_all_messages_as_seen
from core.exceptions import BarelyAnException
from rest_framework import status
from user.utils_relationship import is_blocking as user_is_blocking, is_blocked as user_is_blocked  
from user.constants import USER_ID_OVERLOARDS
from .constants import NO_OF_MSG_TO_LOAD
from django.core.cache import cache
import logging

class LoadConversationsView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        # Get the user from the request
        user = request.user
        # Get all conversations where the user is a member
        conversation_memberships = ConversationMember.objects.filter(user=user)
        conversations = [membership.conversation for membership in conversation_memberships]

        # Serialize only the conversation id and name
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        if not serializer.data or len(serializer.data) == 0:
            return success_response(_('No conversations found'), status_code=status.HTTP_202_ACCEPTED)
        return success_response(_('Conversations loaded successfully'), data=serializer.data)

class LoadConversationView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request, conversation_id=None):
        user = request.user
        msgid = int(request.GET.get('msgid', 0))

        conversation = self.get_conversation(conversation_id)
        self.validate_conversation_membership(conversation, user)
    
        if conversation.is_group_conversation:
            return error_response(_('Group chats are not supported yet'), status_code=status.HTTP_400_BAD_REQUEST)

        # Determine blocking status
        theOverloards = User.objects.get(id=USER_ID_OVERLOARDS)
        other_user = self.get_other_user(conversation, user, theOverloards)
        other_user_online = cache.get(f'user_online_{other_user.id}', False)
        is_blocking = user_is_blocking(user.id, other_user.id)
        is_blocked = user_is_blocked(user.id, other_user.id)

        # Fetch and process messages
        messages_queryset = self.get_messages_queryset(conversation, msgid)
        messages, last_seen_msg, unseen_messages = self.process_messages(messages_queryset)

        # Blackout messages if blocking
        if is_blocking:
            for message in messages:
                message.content = _('**This message is hidden because you are blocking the user**')

        # Add separator messages if needed
        messages_with_separator = self.add_separator_message(messages, last_seen_msg, unseen_messages)

        # Mark as seen
        if not is_blocking:
            mark_all_messages_as_seen(user.id, conversation.id)

        # Serialize messages
        serialized_messages = MessageSerializer(messages_with_separator, many=True)

        # Get the conversation avatar and name
        conversation_avatar = self.get_conversation_avatar(conversation, other_user)
        conversation_name = self.get_conversation_name(conversation, other_user)

        # Prepare the response
        response_data = self.prepare_response(conversation, user, serialized_messages, other_user_online, is_blocking, is_blocked, conversation_avatar, conversation_name)

        return success_response(_('Messages loaded successfully'), **response_data)

    def get_conversation(self, conversation_id):
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise BarelyAnException(_('Conversation not found'), status_code=status.HTTP_404_NOT_FOUND)

    def validate_conversation_membership(self, conversation, user):
        try:
            return ConversationMember.objects.get(conversation=conversation, user=user)
        except ConversationMember.DoesNotExist:
            raise BarelyAnException(_('You are not a member of this conversation'), status_code=status.HTTP_403_FORBIDDEN)

    def get_other_user(self, conversation, user, theOverloards):
        other_member = conversation.members.exclude(Q(user=user) | Q(user=theOverloards)).first()
        if other_member:
            return other_member.user
        raise BarelyAnException(_('No other users found in the conversation'), status_code=status.HTTP_400_BAD_REQUEST)

    def get_messages_queryset(self, conversation, msgid):
        queryset = Message.objects.filter(conversation=conversation)
        if msgid:
            if not queryset.filter(id=msgid).exists():
                raise BarelyAnException(_('Message not found'), status_code=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(id__lt=msgid)
        queryset = queryset.order_by('-created_at')
        return queryset
    
    def process_messages(self, messages_queryset):
        last_seen_msg = messages_queryset.filter(seen_at__isnull=False).order_by('-seen_at').first()
        unseen_messages = messages_queryset.filter(seen_at__isnull=True)
        messages = messages_queryset[:NO_OF_MSG_TO_LOAD]
        return messages, last_seen_msg, unseen_messages
   
    def add_separator_message(self, messages, last_seen_msg, unseen_messages):
        if unseen_messages.exists():
            messages_with_separator = []
            for message in messages:
                if last_seen_msg and message.id == last_seen_msg.id:
                    # Add separator message
                    overlords = User.objects.get(id=USER_ID_OVERLOARDS)
                    # Here we create a fake message wich is not stored in the db
                    # It is really important to keep the structure of this
                    # message the same as the Message Model so that the
                    # MessageSerializer can serialize it correctly
                    messages_with_separator.append({
                        "id": None,
                        "user": overlords,
                        "created_at": last_seen_msg.created_at,
                        "seen_at": None,
                        "content": _("We know that you haven't seen the messages below...")
                    })
                messages_with_separator.append(message)
            return messages_with_separator
        return messages

    def get_conversation_avatar(self, conversation, other_user):
        if conversation.is_group_conversation:
            return 'CHAT_AVATAR_GROUP_DEFAULT' 
        if other_user.avatar_path:
            return other_user.avatar_path
        return 'DEFAULT_AVATAR'

    def get_conversation_name(self, conversation, other_user):
        if conversation.is_group_conversation:
            return conversation.name
        return other_user.username

    def prepare_response(self, conversation, user, serialized_messages, other_user_online, is_blocking, is_blocked, conversation_avatar, conversation_name):
        members = conversation.members.all()
        member_ids = members.values_list('id', flat=True)

        return {
            "conversationId": conversation.id,
            "isBlocked": is_blocked,
            "isBlocking": is_blocking,
            "isGroupChat": conversation.is_group_conversation,
            "isEditable": conversation.is_editable,
            "conversationName": conversation_name,
            "conversationAvatar": conversation_avatar,
            "online": other_user_online,
            "userIds": list(member_ids),
            "data": serialized_messages.data,
        }

class CreateConversationView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        user = request.user
        userIds = request.data.get('userIds', [])
        initialMessage = request.data.get('initialMessage')
        conversation_name = request.data.get('name', None)
        if not userIds:
           return error_response(_("No 'userIds' provided"), status_code=400)
        if not initialMessage:
           return error_response(_("No 'initialMessage' provided"), status_code=400)
        if len(userIds) == 0:
            return error_response(_("No 'userIds' provided"), status_code=400)
        if len(userIds) == 1:
            # A PM conversation
            is_group_conversation = False
            other_user_id = userIds[0]
            other_user = User.objects.get(id=other_user_id)
            # Check if the conversation already exists
            conversation_member = ConversationMember.objects.filter(Q(user=user) | Q(user=other_user),conversation__is_group_conversation=False)
            if conversation_member.exists():
                conversation_id = conversation_member.first().conversation.id
                return success_response(_('Conversation already exists'), data={'conversation_id': conversation_id})
        elif len(userIds) > 1:
            # A group conversation
            if not conversation_name:
                return error_response(_("No 'name' provided"), status_code=400)
            is_group_conversation = True
        
        # Start a transaction to make sure all database operations happen together
        with transaction.atomic():
            # Create the Conversation
            new_conversation = Conversation.objects.create(name=conversation_name, is_group_conversation=is_group_conversation, is_editable=True)
            ConversationMember.objects.create(user=user, conversation=new_conversation)
            if is_group_conversation:
                for userId in userIds:
                    other_user = User.objects.get(id=userId)
                    ConversationMember.objects.create(user=other_user, conversation=new_conversation)
            else:
                ConversationMember.objects.create(user=other_user, conversation=new_conversation)
            Message.objects.create(user=user, conversation=new_conversation, content=initialMessage)

        return success_response(_('Conversation created successfully'), data={'conversation_id': new_conversation.id})
    









































################################################################################
# BELOW IS OLD CODE!!!
################################################################################

## TODO: remove - this is for the test chat page
#def test_chat(request):
#    return render(request, 'chat/test-chat.html')
#
#class ListConversationsView(BaseAuthenticatedView):
#    #authentication_classes = [JWTAuthentication]  # This tells Django to use JWT authentication
#    #permission_classes = [IsAuthenticated]  # This tells Django to require authentication to access this view
#    permission_classes = [AllowAny] #TODO: implement the token-based authentication!
#    
#    def get(self, request, *args, **kwargs):
#        user = request.user
#        
#        # Get all conversations where the user is a member
#        conversation_memberships = ConversationMember.objects.filter(user=user)
#        conversations = [membership.conversation for membership in conversation_memberships]
#        
#        # Serialize only the conversation id and name
#        serializer = ConversationSerializer(conversations, many=True)
#        return Response(serializer.data)
#
## Create a conversation and add members
## If conversation already exists, return the conversation_id
#class CreateConversationView(BaseAuthenticatedView):
#    permission_classes = [AllowAny] #TODO: implement the token-based authentication!
#    @barely_handle_exceptions
#    def post(self, request):
#        from user.models import User
#        sender_id = request.data.get('sender_id')
#        receiver_id = request.data.get('receiver_id')
#
#        # Validate that sender and receiver exist
#        try:
#            sender = User.objects.get(id=sender_id)
#        except User.DoesNotExist:
#            return Response({'error': f'Invalid sender id: {sender_id}'}, status=status.HTTP_400_BAD_REQUEST)
#
#        try:
#            receiver = User.objects.get(id=receiver_id)
#        except User.DoesNotExist:
#            return Response({'error': f'Invalid receiver id: {receiver_id}'}, status=status.HTTP_400_BAD_REQUEST)
#
#        # Check if sender and receiver are the same
#        if sender == receiver:
#            return Response({'error': 'Sender and receiver cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
#        
#        # Check if a conversation between these two users already exists
#        # TODO: SHOULD BE FINE FOR NOW, BUT NEEDS TO BE FIXED IF WE INTRODUCE GROUP CHATS
#        # Get the conversation IDs where the sender is a member
#        sender_conversations = ConversationMember.objects.filter(user=sender).values_list('conversation_id', flat=True)
#
#        # Check if the receiver is in any of the same conversations # TODO: wich isn't a group chat
#        existing_conversation = ConversationMember.objects.filter(user=receiver, conversation__in=sender_conversations).first()
#
#        # If the conversation exists, return the conversation information
#        if existing_conversation:
#            conversation = existing_conversation.conversation  # Get the conversation object from the ConversationMember instance
#            return Response({'conversation_id': conversation.id, 'name': conversation.name}, status=status.HTTP_200_OK)
#        
#        # Start a transaction to make sure all database operations happen together
#        try:
#            with transaction.atomic():
#                # Create the Conversation
#                conversation_name = f'{sender.username} blasphemes with {receiver.username}'
#                conversation_serializer = ConversationSerializer(data={'name': conversation_name})
#
#                if conversation_serializer.is_valid():
#                    conversation = conversation_serializer.save()  # Conversation is created
#                else:
#                    return Response(conversation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#                # Add sender and receiver to the ConversationMember table
#                conversation_member_serializer_sender = ConversationMemberSerializer(data={'conversation': conversation.id, 'user': sender.id})
#                if conversation_member_serializer_sender.is_valid():
#                    conversation_member_serializer_sender.save()
#                else:
#                    raise Exception('Error adding sender to conversation members')
#
#                conversation_member_serializer_receiver = ConversationMemberSerializer(data={'conversation': conversation.id, 'user': receiver.id})
#                if conversation_member_serializer_receiver.is_valid():
#                    conversation_member_serializer_receiver.save()
#                else:
#                    raise Exception('Error adding receiver to conversation members')
#
#            # If everything is successful, return a success response
#            return Response({'conversation_id': conversation.id, 'name': conversation.name}, status=status.HTTP_201_CREATED)
#
#        except Exception as e:
#            # If any error occurs during the transaction, rollback and return an error
#            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#class RenameConversationView(BaseAuthenticatedView):
#    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!
#    @barely_handle_exceptions
#    def post(self, request):
#
#        conversation_id = request.data.get('conversation_id')
#        # Try to get the conversation object
#        try:
#            conversation = Conversation.objects.get(id=conversation_id)
#        except Conversation.DoesNotExist:
#            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
#
#        # Get the new name from the request data
#        new_name = request.data.get('new_name')
#
#        # Perform a simple validation to check if the name is empty
#        if not new_name or not new_name.strip():
#            return Response({'error': 'New conversation name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
#
#        # If valid, update the conversation name
#        conversation.name = new_name
#        conversation.save()
#
#        return Response({'conversation_id': conversation.id, 'new_name': conversation.name}, status=status.HTTP_200_OK)
#
## Send a message
#class SendMessageView(BaseAuthenticatedView):
#    permission_classes = [AllowAny]  # This allows anyone to access this view #TODO: implement the token-based authentication!
#    @barely_handle_exceptions    
#    def post(self, request):
#        from user.models import User
#        sender_id = request.data.get('sender_id')
#        conversation_id = request.data.get('conversation_id')
#        content = request.data.get('content')
#
#        # Check if the sender exists
#        try:
#            sender = User.objects.get(id=sender_id)
#        except User.DoesNotExist:
#            return Response({'error': f'Invalid sender id: {sender_id}'}, status=status.HTTP_400_BAD_REQUEST)
#        
#        # Check if the conversation exists
#        try:
#            conversation = Chat.objects.get(id=conversation_id)
#        except Chat.DoesNotExist:
#            return Response({'error': f'Invalid conversation id: {conversation_id}'}, status=status.HTTP_400_BAD_REQUEST)
#        
#        # Check if the sender is a member of the conversation
#        try:
#            ConversationMember.objects.get(conversation=conversation, user=sender)
#        except ConversationMember.DoesNotExist:
#            return Response({'error': 'Sender is not a member of the conversation'}, status=status.HTTP_400_BAD_REQUEST)
#        
#        # Check if the content is empty
#        if not content or not content.strip():
#            return Response({'error': 'Message content cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
#                            
#        # Create the message
#        message = MessageSerializer(data={'sender': sender.id, 'conversation': conversation.id, 'content': content})
#        if message.is_valid():
#            message = message.save()
#        else:
#            return Response(message.errors, status=status.HTTP_400_BAD_REQUEST)
#
#        return Response({'message_id': message.id, 'content': message.content}, status=status.HTTP_201_CREATED)
#
#class ShowConversationView(BaseAuthenticatedView):
#    permission_classes = [AllowAny]  #TODO: implement the token-based authentication!
#    @barely_handle_exceptions
#    def post(self, request):
#        
#
#         # Create a simple HTML structure to return the messages
#        html_content = f"""
#        <html>
#            <head>
#                <style>
#                    .message-container {{ max-width: 600px; margin: 0 auto; padding: 10px; }}
#                    .message {{ padding: 10px; margin-bottom: 10px; border-radius: 10px; max-width: 80%; }}
#                    .message-left {{ text-align: left; background-color: #f1f1f1; float: left; clear: both; }}
#                    .message-right {{ text-align: right; background-color: #d1e7dd; float: right; clear: both; }}
#                    .timestamp {{ font-size: 0.8em; color: gray; margin-top: 5px; }}
#                </style>
#            </head>
#            <body>
#                <div class="message-container">
#                    <h3>Last 10 Messages in Chat (id:{conversation.id}):</h3>
#                    <h2>»{conversation.name}« </h2>
#                    <ul style="list-style-type: none; padding: 0;">
#        """
#
#        # Loop over the messages and format them
#        for message in messages:
#            # Format the timestamp
#            formatted_time = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
#
#            # Check if the message was sent by the current sender
#            if message.user.id == sender_id:
#                alignment = "message-right"
#            else:
#                alignment = "message-left"
#
#            # Add each message to the HTML with conditional alignment
#            html_content += f"""
#                <li class="message {alignment}">
#                    <strong>{message.user.username}:</strong> {message.content}
#                    <div class="timestamp">{formatted_time}</div>
#                </li>
#            """
#
#        # Close the HTML content
#        html_content += """
#                    </ul>
#                </div>
#            </body>
#        </html>
#        """
#
#        return HttpResponse(html_content, content_type='text/html')
#