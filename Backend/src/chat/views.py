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
from user.utils_relationship import is_blocking as user_is_blocking, is_blocked as user_is_blocked
# Chat
from chat.constants import NO_OF_MSG_TO_LOAD
from chat.models import Conversation, ConversationMember, Message
from chat.serializers import ConversationSerializer, ConversationMemberSerializer, MessageSerializer
from chat.utils import create_conversation, get_conversation_id, mark_all_messages_as_seen_sync, generate_template_msg

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
            return success_response(_('No conversations found. Use the searchbar on the navigation bar to find a user. Then on the profile click on the letter symbol to start a conversation!'), status_code=status.HTTP_202_ACCEPTED)
        return success_response(_('Conversations loaded successfully'), data=serializer.data)

class LoadConversationView(BaseAuthenticatedView):
    #@barely_handle_exceptions TODO: remove comment
    def put(self, request, conversation_id=None):
        user = request.user
        msgid = int(request.GET.get('msgid', 0))
        if(msgid < 0):
            return error_response(_('No more messages to load'), status_code=status.HTTP_400_BAD_REQUEST)

        conversation = self.get_conversation(conversation_id)
        self.validate_conversation_membership(conversation, user)

        # Determine blocking status
        the_overloards = User.objects.get(id=USER_ID_OVERLORDS)
        other_user = self.get_other_user(conversation, user, the_overloards)
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


        # Add separator messages if needed (if there are unseen messages)
        messages = self.add_separator_message(messages, last_seen_msg, unseen_messages)

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
                    # Add separator message
                    # Here we create a fake message wich is not stored in the db
                    # It is really important to keep the structure of this
                    # message the same as the Message Model so that the
                    # MessageSerializer can serialize it correctly
                    messages.insert(i, {
                        "id": None,
                        "user": the_overloards,
                        "created_at": last_seen_msg.created_at,
                        "seen_at": None,
                        "content": _("We know that you haven't seen the messages below...")
                    })
                    i += 1
                    length += 1

            # Blackout messages if blocking
            if is_blocking and message.user == other_user:
                message.content = _('**This message is hidden because you are blocking the user**')
            else:
                # There are two parsings that need to be done in this order:
                # 1. translate template messages e.g:
                #   **B,requester,requestee** -> User @{requester_id} has blocked @{requestee_id}."
                if message.content.startswith('**') and message.content.endswith('**'):
                    message.content = generate_template_msg(message.content)
                # 2. @{user_id} -> @{user_name}@{user_id}@
                if '@' in message.content:
                    numbers_found = []

                    def replacer(match):
                        id_value = match.group(1)
                        numbers_found.append(id_value)
                        try:
                            user = User.objects.get(id=id_value)
                            return f'@{user.username}@{id_value}@'
                        except User.DoesNotExist:
                            return match.group(0)

                    message.content = re.sub(r'@(\d+)', replacer, message.content)
            i += 1

                #TODO:
                #for message in messages:
                #    if message.content.startswith('**invite/') and message.content.endswith('**'):
                #        try:
                #            # Parse the message e.g. **inviter=10,receiver=9,gameid=#76**
                #            message_parts = message.content[2:-2].split('/')
                #            inviter_id = int(message_parts[1])
                #            receiver_id = int(message_parts[2])
                #            game_id = int(message_parts[3])
                #            logging.info(f'Parsed invite message: inviter={inviter_id}, receiver={receiver_id}, gameid={game_id}')
                #            # Get usernames
                #            inviter_name = User.objects.get(id=inviter_id).username
                #            receiver_name = User.objects.get(id=receiver_id).username
                #            # Format the message
                #            message.content = _('@{inviter_name}@{inviter_id}@ invited @{receiver_name}@{receiver_id}@ to a friendly match: #G#{game_id}#').format(
                #                    inviter_name=inviter_name,
                #                    inviter_id=inviter_id,
                #                    receiver_name=receiver_name,
                #                    receiver_id=receiver_id,
                #                    game_id=game_id)
                #        except Exception as e:
                #            logging.error(f'Error parsing invite message ({message.content}): {e}')


        # Mark as seen
        if not is_blocking:
            mark_all_messages_as_seen_sync(user.id, conversation.id)

        new_unread_counter = ConversationMember.objects.get(conversation=conversation, user=user).unread_counter
        new_unread_counter_total = ConversationMember.objects.filter(user=user).aggregate(total_unread_counter=Sum('unread_counter'))['total_unread_counter']

        # Serialize messages
        serialized_messages = MessageSerializer(messages, many=True)

        # Get the conversation avatar and name
        conversation_avatar = self.get_conversation_avatar(conversation, other_user)
        conversation_name = self.get_conversation_name(conversation, other_user)

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

    def process_messages(self, user, messages_queryset):
        last_seen_msg = messages_queryset.filter(seen_at__isnull=False).order_by('-seen_at').first()
        # Exclude the user from unseen messages because they can't miss their own messages.
        unseen_messages = messages_queryset.filter(seen_at__isnull=True).exclude(user=user)
        messages = messages_queryset[:NO_OF_MSG_TO_LOAD]
        return messages, last_seen_msg, unseen_messages

    def add_separator_message(self, messages, last_seen_msg, unseen_messages):
        if not messages:
            return messages
        if unseen_messages.exists():
            messages_with_separator = []
            for message in messages:
                if last_seen_msg and message.id == last_seen_msg.id:
                    # Add separator message
                    overlords = User.objects.get(id=USER_ID_OVERLORDS)
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
        return 'AVATAR_DEFAULT'

    def get_conversation_name(self, conversation, other_user):
        if conversation.is_group_conversation:
            return conversation.name
        return other_user.username

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

class CreateConversationView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        user = request.user
        userIds = request.data.get('userIds', [])
        initialMessage = request.data.get('initialMessage', '').strip()
        conversation_name = request.data.get('name', None)
        if not userIds:
           return error_response(_("No 'userIds' provided"), status_code=status.HTTP_400_BAD_REQUEST)
        if not initialMessage:
           return error_response(_("No 'initialMessage' provided"), status_code=status.HTTP_400_BAD_REQUEST)
        if len(userIds) == 0:
            return error_response(_("No 'userIds' provided"), status_code=status.HTTP_400_BAD_REQUEST)
        if len(userIds) == 1:
            # A PM conversation
            is_group_conversation = False
            other_user_id = userIds[0]
            try:
                other_user = User.objects.get(id=other_user_id)
            except User.DoesNotExist:
                return error_response(_("User not found"), status_code=status.HTTP_404_NOT_FOUND)
            # TODO: somewehre here create the message: **S,requester,requestee**
            # Check if the user blocked client
            if is_blocked(user.id, other_user.id):
                return error_response(_("You are blocked by the user"), status_code=status.HTTP_403_FORBIDDEN)
            # Check if the conversation already exists
            conversation_id = get_conversation_id(user, other_user)
            if conversation_id:
                return error_response(_('Conversation already exists'), **{'conversationId': conversation_id})
        elif len(userIds) > 1:
            error_response(_("Group chats are not supported (yet)"), status_code=status.HTTP_400_BAD_REQUEST)

        # Create the conversation
        new_conversation = create_conversation(user, other_user, initialMessage, user)

        return success_response(_('Conversation created successfully'), **{'conversationId': new_conversation.id})
