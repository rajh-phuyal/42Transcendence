# Basics
import logging
# Django
from rest_framework import status
from django.utils.translation import gettext as _
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()
# Services
from services.send_ws_msg import TempConversationMessage, send_ws_badge, send_ws_badge_all, send_ws_chat
# Core
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.decorators import barely_handle_exceptions
from core.exceptions import BarelyAnException
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
from user.utils_relationship import is_blocking as user_is_blocking, is_blocked as user_is_blocked
# Chat
from chat.constants import NO_OF_MSG_TO_LOAD
from chat.models import Conversation, ConversationMember, Message
from chat.serializers import ConversationsSerializer, MessageSerializer
from chat.utils import validate_conversation_membership, get_other_user
from chat.message_utils import mark_all_messages_as_seen, create_msg_db
from chat.conversation_utils import get_or_create_conversation

class LoadConversationsView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        # Get the user from the request
        user = request.user
        # Get all conversations where the user is a member
        conversation_memberships = ConversationMember.objects.filter(user=user)
        conversations = [membership.conversation for membership in conversation_memberships]
        # Serialize the conversations
        serializer = ConversationsSerializer(conversations, many=True, context={'user': user})
        if not serializer.data or len(serializer.data) == 0:
            return success_response(_('No conversations found. Use the searchbar on the navigation bar to find a user. Then on the profile click on the letter symbol to start a conversation!'), status_code=status.HTTP_202_ACCEPTED)
        return success_response(_('Conversations loaded successfully'), data=serializer.data)

class LoadConversationView(BaseAuthenticatedView):
    """
    This function fetches the last X messages from a conversation togehter with
    details about the conversation. It also marks all messages as seen and blackouts
    messages if the user is blocking the other user. This function is not ideal
    I guess using a new Serializer for the conversation would be better...
    """
    #@barely_handle_exceptions TODO: remove comment
    def put(self, request, conversation_id=None):
        user = request.user
        msgid = int(request.GET.get('msgid', 0))
        if(msgid < 0):
            return error_response(_('No more messages to load'), status_code=status.HTTP_400_BAD_REQUEST)
        conversation =  Conversation.objects.get(id=conversation_id)
        validate_conversation_membership(user, conversation)
        # Determine blocking status
        the_overloards = User.objects.get(id=USER_ID_OVERLORDS)
        other_user = get_other_user(user, conversation)
        is_blocking = user_is_blocking(user.id, other_user.id)
        is_blocked = user_is_blocked(user.id, other_user.id)
        # Fetch Messages
        queryset = Message.objects.filter(conversation=conversation)
        if msgid:
            if not queryset.filter(id=msgid).exists():
                raise BarelyAnException(_('Message not found'), status_code=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(id__lt=msgid)
        queryset = queryset.order_by('-created_at')
        last_seen_msg = queryset.filter(seen_at__isnull=False).order_by('-seen_at').first()
        # Exclude the user from unseen messages because they can't miss their own messages.
        unseen_messages = queryset.filter(seen_at__isnull=True).exclude(user=user)
        messages = queryset[:NO_OF_MSG_TO_LOAD]
        if not messages:
            return error_response(_('No more messages to load'), status_code=status.HTTP_400_BAD_REQUEST)
        # Transform messages to list
        messages = list(messages)
        i = 0
        length = len(messages)
        while i < length:
            message = messages[i]
            # If needed add separator message
            if unseen_messages.exists() and last_seen_msg and message.id == last_seen_msg.id:
                    messages.insert(i, TempConversationMessage(overlords_instance=the_overloards,
                       conversation=conversation,
                       created_at=last_seen_msg.created_at,
                       content= _("We know that you haven't seen the messages below..."))
                       )
                    i += 1
                    length += 1
            # Blackout messages if blocking
            if is_blocking and message.user == other_user:
                message.content = _('This message is hidden because you are blocking the user')
            i += 1
        # Mark as seen
        mark_all_messages_as_seen(user, conversation)
        # Serialize messages
        logging.info(f"Messages before serialization: {messages}")
        serialized_messages = MessageSerializer(messages, many=True)
        logging.info(f"Messages after serialization: {serialized_messages.data}")
        # Get the conversation avatar and name
        conversation_avatar = other_user.avatar_path
        conversation_name = other_user.username
        # Prepare the response
        response_data = {
            "conversationId": conversation.id,
            "isBlocked": is_blocked,
            "isBlocking": is_blocking,
            "isGroupChat": conversation.is_group_conversation,
            "isEditable": conversation.is_editable,
            "conversationName": conversation_name,
            "conversationAvatar": conversation_avatar,
            "online": other_user.get_online_status(),
            "userId": other_user.id,
            "data": serialized_messages.data,
        }
        return success_response(_('Messages loaded successfully'), **response_data)

class CreateConversationView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        user = request.user
        other_user_id = request.data.get('userId', None)
        initial_message = request.data.get('initialMessage', '').strip()
        initial_message = initial_message.strip('*') # Messages are not allowed to start or end with a "*" because it's used for template messages
        if initial_message.startswith('/'):
            raise BarelyAnException(_("You can't use commands in the initial message"), status_code=status.HTTP_400_BAD_REQUEST)
        if not other_user_id:
           return error_response(_("No 'userId' provided"), status_code=status.HTTP_400_BAD_REQUEST)
        if not initial_message:
           return error_response(_("No 'initialMessage' provided"), status_code=status.HTTP_400_BAD_REQUEST)

        if user_is_blocked(user.id, other_user_id):
            return error_response(_("You are blocked by the user"), status_code=status.HTTP_403_FORBIDDEN)

        # Get / Create conversation
        conversation = get_or_create_conversation(user, other_user_id)
        # Create message
        message_object = create_msg_db(user, conversation, initial_message)
        # Send update badge count of other user
        async_to_sync(send_ws_badge)(other_user_id, conversation.id)
        async_to_sync(send_ws_badge_all)(other_user_id)
        # Send the message to the channel
        async_to_sync(send_ws_chat)(message_object)

        return success_response(_('Conversation created (or found) and delivered initial message.'), **{'conversationId': conversation.id})
