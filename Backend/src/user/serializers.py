from django.db.models import Q
from .models import User, IsCoolWith
from rest_framework import serializers
from .utils_relationship import get_relationship_status

# This will prepare the data to be sent to the frontend as JSON
class ProfileSerializer(serializers.ModelSerializer):
    # Add fields that will return dummy data for now
    avatarUrl = serializers.CharField(source='avatar_path', default='default_avatar.png')
    firstName = serializers.CharField(source='first_name', default="John")
    lastName = serializers.CharField(source='last_name', default="Doe")
    online = serializers.BooleanField(default=False)
    lastLogin = serializers.CharField(default="YYYY-MM-DD hh:mm")
    language = serializers.CharField(default="en")
    chatId = serializers.CharField(default=42)
    newMessage = serializers.BooleanField(default=True)
    
    # Add relationship field
    relationship = serializers.SerializerMethodField()
    # Add the stats section with dummy data
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

class FriendListSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.CharField(source='avatar_path', default='default_avatar.png')
    online = serializers.BooleanField(source='is_active', default=False)
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatarUrl', 'online', 'status']
    
    def get_status(self, obj):
        # Retrieve the user from the URL (passed to serializer context by the view)
        url_user = self.context['request'].user
        WROGN USER HERE!

        # Check the relationship status where the URL user is either requester or requestee
        try:
            relationship = IsCoolWith.objects.get(
                (Q(requester=url_user, requestee=obj) | Q(requester=obj, requestee=url_user))
            )
            return relationship.status
        except IsCoolWith.DoesNotExist:
            return None  # No relationship found