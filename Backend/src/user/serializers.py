from django.db.models import Q
from user.models import User, IsCoolWith, CoolStatus
from rest_framework import serializers
from user.utils_relationship import get_relationship_status

# This will prepare the data for endpoint '/user/profile/<int:id>/'
class ProfileSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.CharField(source='avatar_path', default='default_avatar.png')
    firstName = serializers.CharField(source='first_name', default="John")
    lastName = serializers.CharField(source='last_name', default="Doe")
    online = serializers.BooleanField(default=False)
    lastLogin = serializers.CharField(default="YYYY-MM-DD hh:mm")
    language = serializers.CharField(default="en")
    chatId = serializers.CharField(default=42)
    newMessage = serializers.BooleanField(default=True)
    relationship = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
                # id and username are the same key than in the model.py, thats why i dont need them in the above section
        fields = ['id', 'username', 'avatarUrl', 'firstName', 'lastName', 'online', 'lastLogin', 'language', 'chatId', 'newMessage', 'relationship', 'stats']
    
    # Valid types are 'yourself' 'noFriend', 'friend', 'requestSent', 'requestReceived'
    def get_relationship(self, obj):
        # `requester` is the current authenticated user
        requester = self.context['request'].user  
        # `requested` is the user object being serialized (from the URL)
        requested = obj
        return get_relationship_status(requester, requested)
    
    def get_stats(self, obj):
        return {
            "game": {
                "won": 42,
                "played": 420
            },
            "tournament": {
                "firstPlace": 5,
                "secondPlace": 6,
                "thirdPlace": 7,
                "played": 42
            },
            "score": {
                "skill": 0.10,
                "experience": 0.25,
                "performance": 0.75,
                "total": 0.50
            }
        }

# This will prepare the data for endpoint '/user/friend/list/<int:id>/'
class ListFriendsSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatarUrl = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = IsCoolWith
        fields = ['id', 'username', 'avatarUrl', 'status']

    def get_other_user(self, obj):
        user_id = self.context.get('user_id')
        return obj.requestee if obj.requester.id == user_id else obj.requester

    def get_id(self, obj):
        other_user = self.get_other_user(obj)
        return other_user.id

    def get_username(self, obj):
        other_user = self.get_other_user(obj)
        return other_user.username

    def get_avatarUrl(self, obj):
        other_user = self.get_other_user(obj)
        return other_user.avatar_path

    def get_status(self, obj):
        user_id = self.context.get('user_id')
        if obj.status == CoolStatus.PENDING:
            return 'requestSend' if obj.requester.id == user_id else 'requestReceived'
        return 'accepted'