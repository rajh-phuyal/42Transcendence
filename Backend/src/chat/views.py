from services.chat_service import send_conversation_unread_counter, send_total_unread_counter
from django.db.models import Q
from django.db.models import Sum
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
from .utils import mark_all_messages_as_seen_sync
from core.exceptions import BarelyAnException
from rest_framework import status
from user.utils_relationship import is_blocking as user_is_blocking, is_blocked as user_is_blocked  
from user.constants import USER_ID_OVERLOARDS
from .constants import NO_OF_MSG_TO_LOAD
from django.core.cache import cache
from asgiref.sync import async_to_sync

import logging
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
from services.websocket_utils import send_message_to_user_sync

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
        from services.websocket_utils import send_message_to_user
        user = request.user
        msgid = int(request.GET.get('msgid', 0))

        conversation = self.get_conversation(conversation_id)
        self.validate_conversation_membership(conversation, user)
    
        if conversation.is_group_conversation:
            return error_response(_('Group chats are not supported yet'), status_code=status.HTTP_400_BAD_REQUEST)

        # Determine blocking status
        the_overloards = User.objects.get(id=USER_ID_OVERLOARDS)
        other_user = self.get_other_user(conversation, user, the_overloards)
        other_user_online = cache.get(f'user_online_{other_user.id}', False)
        is_blocking = user_is_blocking(user.id, other_user.id)
        is_blocked = user_is_blocked(user.id, other_user.id)

        # Fetch and process messages
        messages_queryset = self.get_messages_queryset(conversation, msgid)
        messages, last_seen_msg, unseen_messages = self.process_messages(messages_queryset)

        # Blackout messages if blocking
        if is_blocking:
            for message in messages:
                if message.user != user:
                    message.content = _('**This message is hidden because you are blocking the user**')

        # Add separator messages if needed
        messages_with_separator = self.add_separator_message(messages, last_seen_msg, unseen_messages)

        # Mark as seen
        if not is_blocking:
            mark_all_messages_as_seen_sync(user.id, conversation.id)

        new_unread_counter = ConversationMember.objects.get(conversation=conversation, user=user).unread_counter
        new_unread_counter_total = ConversationMember.objects.filter(user=user).aggregate(total_unread_counter=Sum('unread_counter'))['total_unread_counter']

        # Serialize messages
        serialized_messages = MessageSerializer(messages_with_separator, many=True)

        # Get the conversation avatar and name
        conversation_avatar = self.get_conversation_avatar(conversation, other_user)
        conversation_name = self.get_conversation_name(conversation, other_user)

        # Prepare the response
        response_data = self.prepare_response(conversation,
                                              user, 
                                              serialized_messages, 
                                              other_user_online,
                                              is_blocking,
                                              is_blocked,
                                              conversation_avatar,
                                              conversation_name,
                                              new_unread_counter,
                                              new_unread_counter_total)

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

    def get_other_user(self, conversation, user, the_overloards):
        other_member = conversation.members.exclude(Q(user=user) | Q(user=the_overloards)).first()
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

    def prepare_response(self, conversation, user, serialized_messages, other_user_online, is_blocking, is_blocked, conversation_avatar, conversation_name, new_unread_counter, new_unread_counter_total):
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
            "conversationUnreadCounter": new_unread_counter,
            "totalUnreadCounter": new_unread_counter_total,
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
            user_conversations = ConversationMember.objects.filter(
                user=user.id,
                conversation__is_group_conversation=False,
            ).values_list('conversation_id', flat=True)

            other_user_conversations = ConversationMember.objects.filter(
                user=other_user.id,
                conversation__is_group_conversation=False
            ).values_list('conversation_id', flat=True)

            common_conversations = set(user_conversations).intersection(other_user_conversations)

            if common_conversations:
                conversation_id = common_conversations.pop()
                return success_response(_('Conversation already exists'), **{'conversation_id': conversation_id})
        elif len(userIds) > 1:
            # TODO: #204
            error_response(_("Group chats are not supported yet"), status_code=400)
            # A group conversation
            #if not conversation_name:
            #    return error_response(_("No 'name' provided"), status_code=400)
            #is_group_conversation = True
        
        # Start a transaction to make sure all database operations happen together
        with transaction.atomic():
            # Create the Conversation
            new_conversation = Conversation.objects.create(name=conversation_name, is_group_conversation=is_group_conversation, is_editable=True)
            ConversationMember.objects.create(user=user, conversation=new_conversation)
            # TODO: #204
            #if is_group_conversation:
            #    for userId in userIds:
            #        other_user = User.objects.get(id=userId)
            #        ConversationMember.objects.create(user=other_user, conversation=new_conversation, unread_counter=1)
            #else:
            ConversationMember.objects.create(user=other_user, conversation=new_conversation, unread_counter=1)
            initialMessageObject = Message.objects.create(user=user, conversation=new_conversation, content=initialMessage)

        # Adding the conversation to the user's WebSocket groups (if they are logged in)
        group_name = f"conversation_{new_conversation.id}"
        channel_name_user =  cache.get(f'user_channel_{user.id}', None)
        if channel_name_user:
            async_to_sync(channel_layer.group_add)(group_name, channel_name_user)
        channel_name_other_user =  cache.get(f'user_channel_{other_user.id}', None)
        if channel_name_other_user:
            async_to_sync(channel_layer.group_add)(group_name, channel_name_other_user)
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "messageType": "newConversation",   
                "type": "new_conversation",
                "conversationId": new_conversation.id,
                "isGroupChat": new_conversation.is_group_conversation,
                "isEditable": new_conversation.is_editable,
                "conversationName": user.username,
                "conversationAvatar": user.avatar_path,
                "unreadCounter": 1,
                "online": True,
                "lastUpdate": initialMessageObject.created_at.isoformat(),
                "isEmpty": False
            })
        async_to_sync(send_total_unread_counter)(other_user.id)
        async_to_sync(send_conversation_unread_counter)(other_user.id, new_conversation.id)
        return success_response(_('Conversation created successfully'), **{'conversation_id': new_conversation.id})
