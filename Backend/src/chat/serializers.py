# Basics
import re
# Django
from rest_framework import serializers
from django.utils.translation import gettext as _
# User
from user.constants import AVATAR_DEFAULT
from user.models import User
# Chat
from chat.models import Conversation, Message, ConversationMember
from chat.utils import get_other_user

def generate_template_msg(message):
    """
    This is used to transform a db message.content into a translated string
    Will be only used by the MessageSerializer. e.g:
    **B,12,42** -> User @12 has blocked @42
    """
    message = message[2:-2]
    parts = message.split(',')
    cmd_type = parts[0]
    params = parts[1:]

    message_templates = {
        "G": {
            "message": _("Game with ID {1} has been created."),
            "count": 1
        },
        "GL": {
            "message": _("Local game with ID {1} has been created."),
            "count": 1
        },
        "FS": {
            "message": _("User @{1} has sent a friend request to @{2}."),
            "count": 2
        },
        "FA": {
            "message": _("User @{1} has accepted the friend request from @{2}."),
            "count": 2
        },
        "FC": {
            "message": _("User @{1} has canceled the friend request to @{2}."),
            "count": 2
        },
        "FR": {
            "message": _("User @{1} has rejected the friend request from @{2}."),
            "count": 2
        },
        "FU": {
            "message": _("User @{1} has removed @{2} from their friends list."),
            "count": 2
        },
        "B": {
            "message": _("User @{1} has blocked @{2}."),
            "count": 2
        },
        "U": {
            "message": _("User @{1} has unblocked @{2}."),
            "count": 2
        },
        "S": {
            "message": _("User @{1} has started a conversation with @{2}."),
            "count": 2
        },
        "TI": {
            "message": _("User @{1} has invited @{2} to the tournament: {3}."),
            "count": 3
        },
    }

    if cmd_type not in message_templates:
        raise ValueError(f"Invalid template key: {cmd_type}")

    template = message_templates[cmd_type]
    if len(params) != template["count"]:
        raise ValueError(f"Expected {template['count']} parameters, but got {len(params)}")
class MessageSerializer(serializers.ModelSerializer):
    """
    This is the most powerful serializer in this project. Each chat message
    should be serialized with this class before sending it to the frontend.
    The serializer will first create template messages
        e.g.: **FS,12,42** -> User @12 has sent a friend request to @42:
    and than replace mentions
        e.g: User @12 has sent a friend request to @42 -> User @astein@12@ has sent a friend request to @fdaestr@42@
    """
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
        if not content or '@' not in content:
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
    conversationName = serializers.SerializerMethodField()
    conversationAvatar = serializers.SerializerMethodField()
    unreadCounter = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()
    lastUpdate = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversationId', 'conversationName', 'conversationAvatar', 'unreadCounter', 'online', 'lastUpdate']
    def get_conversationName(self, obj):
        return get_other_user(self.context['user'], obj).username

    def get_conversationAvatar(self, obj):
        return get_other_user(self.context['user'], obj).avatar_path

    def get_unreadCounter(self, obj):
        current_user = self.context['user']
        try:
            conversation_member = obj.members.get(user=current_user)
            return conversation_member.unread_counter
        except ConversationMember.DoesNotExist:
            return 0

    def get_online(self, obj):
        return get_other_user(self.context['user'], obj).get_online_status()

    def get_lastUpdate(self, obj):
        # Fetch the timestamp of the last message in the conversation
        last_message = obj.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else None
