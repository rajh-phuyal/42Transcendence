from rest_framework import serializers
from chat.models import Conversation, ConversationMember, Message
from django.core.cache import cache
from rest_framework import serializers
from .models import Conversation, Message, ConversationMember
from .constants import CHAT_AVATAR_GROUP_DEFAULT
from user.constants import DEFAULT_AVATAR
from django.utils.translation import gettext as _
class ConversationSerializer(serializers.ModelSerializer):
    conversationId = serializers.IntegerField(source='id')
    isGroupChat = serializers.BooleanField(source='is_group_conversation')
    isEditable = serializers.BooleanField(source='is_editable')
    conversationName = serializers.SerializerMethodField()
    conversationAvatar = serializers.SerializerMethodField()
    unreadCounter = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    lastUpdate = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversationId',
            'isGroupChat',
            'isEditable',
            'conversationName',
            'conversationAvatar',
            'unreadCounter',
            'online',
            'lastUpdate',
        ]
    def get_conversationName(self, obj):
        if obj.name:
            return obj.name

        current_user = self.context['request'].user
        try:
            other_member = obj.members.exclude(user=current_user).first()
            if other_member and other_member.user.username:
                return other_member.user.username
        except Exception:
            pass  # If any error occurs, fall through to the fallback

        # Fallback to "Top Secret"
        return _("top secret")

    def get_conversationAvatar(self, obj):
        if obj.is_group_conversation:
            return CHAT_AVATAR_GROUP_DEFAULT
        else:
            current_user = self.context.get('request').user
            other_members = obj.members.exclude(user=current_user)

        if other_members.exists():
            other_user = other_members.first().user
            return other_user.avatar_path if other_user.avatar_path else 'CHAT_AVATAR_DEFAULT'

        # Default avatar in case no other members exist (which should never happen)
        return DEFAULT_AVATAR

    def get_unreadCounter(self, obj):
        current_user = self.context['request'].user
        try:
            conversation_member = obj.members.get(user=current_user)
            return conversation_member.unread_counter
        except ConversationMember.DoesNotExist:
            return 0

    def get_online(self, obj):
        current_user = self.context['request'].user
        if obj.is_group_conversation:
            return False
        else:
            try:
                other_member = obj.members.exclude(user=current_user).first()
                if other_member and cache.get(f'user_online_{other_member.user.id}'):
                    return True
                return False
            except Exception:
                return False

    def get_lastUpdate(self, obj):
        # Fetch the timestamp of the last message in the conversation
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else None

class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = ('__all__')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'