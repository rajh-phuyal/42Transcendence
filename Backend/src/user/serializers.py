from rest_framework import serializers
from .models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']
# 

# This will prepare the data to be sent to the frontend as JSON
class ProfileSerializer(serializers.ModelSerializer):
    # Add fields that will return dummy data for now
    avatarUrl = serializers.URLField(default="http://dummyavatar.url")
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
    
	# TODO: This is dummy and should be replaced with actual data
    # Valid types are 'yourself' 'noFriend', 'friend', 'requestSent', 'requestReceived'
    def get_relationship(self, obj):
        return {
            "state": "yourself",
            "isBlocking": False,
            "isBlocked": False
        }
    
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