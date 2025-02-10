# Basics
import logging, re
# Django
from rest_framework import status
from django.db.models import Q
from django.db.models import Sum
from django.utils.translation import gettext as _
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
# Services
from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
from services.websocket_utils import send_message_to_user_sync
# Core
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.decorators import barely_handle_exceptions
from core.exceptions import BarelyAnException
# User
from user.constants import USER_ID_OVERLORDS
from user.models import User
from user.utils import get_user_by_id
from user.utils_relationship import is_blocking as user_is_blocking, is_blocked as user_is_blocked
# Chat
from chat.constants import NO_OF_MSG_TO_LOAD
from chat.models import Conversation, ConversationMember, Message
from chat.serializers import ConversationsSerializer, ConversationMemberSerializer, MessageSerializer
from chat.utils import create_conversation, get_conversation_id, mark_all_messages_as_seen_sync, LastSeenMessage, validate_conversation_membership, get_other_user

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
class LoadConversationsView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        # Get the user from the request
        user = request.user
        # Get all conversations where the user is a member
        conversation_memberships = ConversationMember.objects.filter(user=user)
        conversations = [membership.conversation for membership in conversation_memberships]

        # Serialize only the conversation id and name
        serializer = ConversationsSerializer(conversations, many=True, context={'request': request})
        if not serializer.data or len(serializer.data) == 0:
            return success_response(_('No conversations found. Use the searchbar on the navigation bar to find a user. Then on the profile click on the letter symbol to start a conversation!'), status_code=status.HTTP_202_ACCEPTED)
        return success_response(_('Conversations loaded successfully'), data=serializer.data)

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
class LoadConversationView(BaseAuthenticatedView):
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
                    messages.insert(i, LastSeenMessage(last_seen_msg.created_at, the_overloards))
                    i += 1
                    length += 1

            # Blackout messages if blocking
            if is_blocking and message.user == other_user:
                message.content = _('**This message is hidden because you are blocking the user**')
            i += 1

        # Mark as seen
        if not is_blocking:
            mark_all_messages_as_seen_sync(user.id, conversation.id)

        new_unread_counter = ConversationMember.objects.get(conversation=conversation, user=user).unread_counter
        new_unread_counter_total = ConversationMember.objects.filter(user=user).aggregate(total_unread_counter=Sum('unread_counter'))['total_unread_counter']

        # Serialize messages
        serialized_messages = MessageSerializer(messages, many=True)

        # Get the conversation avatar and name
        conversation_avatar = self.get_conversation_avatar(conversation, other_user)
        conversation_name = other_user.username

        # Prepare the response
        response_data = self.prepare_response(conversation,
                                              user,
                                              serialized_messages,
                                              other_user,
                                              is_blocking,
                                              is_blocked,
                                              conversation_avatar,
                                              conversation_name,
                                              new_unread_counter,
                                              new_unread_counter_total)

        return success_response(_('Messages loaded successfully'), **response_data)

    def get_messages_queryset(self, conversation, msgid):
        queryset = Message.objects.filter(conversation=conversation)
        if msgid:
            if not queryset.filter(id=msgid).exists():
                raise BarelyAnException(_('Message not found'), status_code=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(id__lt=msgid)
        queryset = queryset.order_by('-created_at')
        return queryset

    def process_messages(self, user, messages_queryset):
        last_seen_msg = messages_queryset.filter(seen_at__isnull=False).order_by('-seen_at').first()
        # Exclude the user from unseen messages because they can't miss their own messages.
        unseen_messages = messages_queryset.filter(seen_at__isnull=True).exclude(user=user)
        messages = messages_queryset[:NO_OF_MSG_TO_LOAD]
        return messages, last_seen_msg, unseen_messages


    def get_conversation_avatar(self, conversation, other_user):
        if conversation.is_group_conversation:
            return 'CHAT_AVATAR_GROUP_DEFAULT'
        if other_user.avatar_path:
            return other_user.avatar_path
        return 'AVATAR_DEFAULT'

    def prepare_response(self, conversation, user, serialized_messages, other_user, is_blocking, is_blocked, conversation_avatar, conversation_name, new_unread_counter, new_unread_counter_total):
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
            "online": other_user.get_online_status(),
            "userId": other_user.id,
            "conversationUnreadCounter": new_unread_counter,
            "totalUnreadCounter": new_unread_counter_total,
            "data": serialized_messages.data,
        }

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
class CreateConversationView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        user = request.user
        other_user_id = request.data.get('userId', None)
        initial_message = request.data.get('initialMessage', '').strip()
        if not other_user_id:
           return error_response(_("No 'userId' provided"), status_code=status.HTTP_400_BAD_REQUEST)
        if not initial_message:
           return error_response(_("No 'initialMessage' provided"), status_code=status.HTTP_400_BAD_REQUEST)

        # A PM conversation (Since we don't support group chats in MVP)
        other_user = get_user_by_id(other_user_id)

        # TODO: somewehre here create the message: **S,requester,requestee**
        # Check if the user blocked client
        if user_is_blocked(user.id, other_user.id):
            return error_response(_("You are blocked by the user"), status_code=status.HTTP_403_FORBIDDEN)
        # Check if the conversation already exists
        conversation_id = get_conversation_id(user, other_user)
        if conversation_id:
            return error_response(_('Conversation already exists'), **{'conversationId': conversation_id})

        # Create the conversation
        new_conversation = create_conversation(user, other_user, initial_message, user)

        return success_response(_('Conversation created successfully'), **{'conversationId': new_conversation.id})
