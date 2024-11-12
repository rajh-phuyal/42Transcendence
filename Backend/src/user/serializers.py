from rest_framework import serializers
from .models import User
from .utils import get_relationship_status
from django.core.cache import cache

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']
# 

# This will prepare the data to be sent to the frontend as JSON
class ProfileSerializer(serializers.ModelSerializer):
    # Add fields that will return dummy data for now
    avatarUrl = serializers.CharField(source='avatar_path', default='default_avatar.png')
    firstName = serializers.CharField(source='first_name', default="John")
    lastName = serializers.CharField(source='last_name', default="Doe")
    online = serializers.SerializerMethodField()
    lastLogin = serializers.SerializerMethodField()
    chatId = serializers.CharField(default=42)
    newMessage = serializers.BooleanField(default=True)
    
    # Add relationship field
    relationship = serializers.SerializerMethodField()
    # Add the stats section with dummy data
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatarUrl', 'firstName', 'lastName', 'online', 'lastLogin', 'language', 'chatId', 'newMessage', 'relationship', 'stats']

    def get_lastLogin(self, obj):
        # Check if `last_login` is None or `online` is True
        if obj.last_login is None or self.get_online(obj):
            return "under surveillance"

        # Otherwise, format `last_login` as 'YYYY-MM-DD hh:mm'
        return obj.last_login.strftime("%Y-%m-%d %H:%M")

    def get_online(self, obj):
        # AI Opponent and Overlords are always online
        if obj.id == 1 or obj.id == 2:
            return True
        # Check if the user's online status is in the cache
        return cache.get(f'user_online_{obj.id}', False)

    # Valid types are 'yourself' 'noFriend', 'friend', 'requestSent', 'requestReceived'
    def get_relationship(self, obj):
        # `requester` is the current authenticated user
        requester = self.context['request'].user  
        
        # `requested` is the user object being serialized (from the URL)
        requested = obj

        # Use the utility function to get the relationship status
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