# Basics
import re
# Django
from rest_framework import serializers
from django.core.cache import cache
from django.utils.translation import gettext as _
# User
from user.constants import AVATAR_DEFAULT
from user.models import User
# Chat
from chat.models import Conversation, Message, ConversationMember
from chat.utils import get_other_user

# This is used to transform a db message.content into a translated string
# Will be used by the MessageSerializer. e.g:
# **B,12,42** -> User @12 has blocked @42
def generate_template_msg(message):
    message = message[2:-2]
    parts = message.split(',')
    cmd_type = parts[0]
    params = parts[1:]

    message_templates = {
        "G": _("Game with ID {gameid} has been created."),
        "GL": _("Local game with ID {gameid} has been created."),
        "FS": _("User @{requester} has sent a friend request to @{requestee}."),
        "FA": _("User @{requester} has accepted the friend request from @{requestee}."),
        "FC": _("User @{requester} has canceled the friend request to @{requestee}."),
        "FR": _("User @{requester} has rejected the friend request from @{requestee}."),
        "FU": _("User @{requester} has removed @{requestee} from their friends list."),
        "B": _("User @{requester} has blocked @{requestee}."),
        "U": _("User @{requester} has unblocked @{requestee}."),
        "S": _("User @{requester} has started a conversation with @{requestee}."),
        "TI": _("User @{requester} has invited @{requestee} to the tournament: {tournament}."),
    }

    if cmd_type in message_templates:
        if cmd_type in ["G", "GL"]:
            return message_templates[cmd_type].format(gameid=params[0])
        elif cmd_type == "TI":
            return message_templates[cmd_type].format(requester=params[0], requestee=params[1], tournament=params[2])
        else:
            return message_templates[cmd_type].format(requester=params[0], requestee=params[1])

    return _("Unknown command.: {message}").format(message=message)

class MessageSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source='user.id', required=False)
    username = serializers.CharField(source='user.username', required=False)
    avatar = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', required=False)
    seenAt = serializers.DateTimeField(source='seen_at', allow_null=True, required=False)
    content = serializers.CharField()
    conversationId = serializers.IntegerField(source='conversation.id', required=False)
    type = serializers.CharField(default="chat_message")
    messageType = serializers.CharField(default="chat")

    class Meta:
        model = Message
        fields = ['id', 'conversationId', 'userId', 'username', 'avatar', 'content', 'createdAt', 'seenAt', 'type', 'messageType']

    def replace_mentions(self, content):
        """
        This will transform @10 to @astein@10@ so that the frontend can display a clickable username
        """
        if '@' not in content:
            return content  # Skip processing if no mentions

        def replacer(match):
            user_id = match.group(1)
            try:
                user = User.objects.get(id=user_id)
                return f'@{user.username}@{user_id}@'
            except User.DoesNotExist:
                return match.group(0)  # Keep original if user not found

        return re.sub(r'@(\d+)', replacer, content)

    def parse_template_messages(self, content):
        """
        This will create a template message if the content is wrapped in ** **
        """
        if content.startswith('**') and content.endswith('**'):
            return generate_template_msg(content)
        return content

    def get_avatar(self, obj):
        if isinstance(obj, dict):  # Custom separator message
            return obj.get('user').avatar_path if obj.get('user') else AVATAR_DEFAULT
        return obj.user.avatar_path if obj.user.avatar_path else AVATAR_DEFAULT

    def to_representation(self, instance):
        if isinstance(instance, dict):  # Handle custom messages (LastSeenMessage)
            content = instance.get("content", "")
        else:
            content = instance.content
        content = self.parse_template_messages(content)
        content = self.replace_mentions(content)

        if isinstance(instance, dict):  # Handle custom dictionary data
            return {
                "id": instance.get("id"),
                "userId": instance["user"].id if instance.get("user") else None,
                "username": instance["user"].username if instance.get("user") else _("System"),
                "avatar": self.get_avatar(instance),
                "content": content,
                "createdAt": instance.get("created_at"),
                "seenAt": instance.get("seen_at"),
            }
        data = super().to_representation(instance)
        data["content"] = content
        return data

# TODO: REMOVE WHEN FINISHED #284
class ConversationsSerializer(serializers.ModelSerializer):
    conversationId = serializers.IntegerField(source='id')
    isEditable = serializers.BooleanField(source='is_editable')
    conversationName = serializers.SerializerMethodField()
    conversationAvatar = serializers.SerializerMethodField()
    unreadCounter = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    lastUpdate = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversationId', 'isEditable', 'conversationName', 'conversationAvatar', 'unreadCounter', 'online', 'lastUpdate']
    def get_conversationName(self, obj):
        return get_other_user(self.context['request'].user, obj).username

    def get_conversationAvatar(self, obj):
        return get_other_user(self.context['request'].user, obj).avatar_path

    def get_unreadCounter(self, obj):
        current_user = self.context['request'].user
        try:
            conversation_member = obj.members.get(user=current_user)
            return conversation_member.unread_counter
        except ConversationMember.DoesNotExist:
            return 0

    def get_online(self, obj):
        return get_other_user(self.context['request'].user, obj).get_online_status()

    def get_lastUpdate(self, obj):
        # Fetch the timestamp of the last message in the conversation
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else None

# TODO: refactor chat/ ws: THIS FUNCTION NEEDS TO BE REVIESED!
# TODO: REMOVE WHEN FINISHED #284
class ConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMember
        fields = ('__all__')
