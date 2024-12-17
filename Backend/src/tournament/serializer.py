from rest_framework import serializers
from .models import TournamentMember

class TournamentMemberSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    userAvatar = serializers.CharField(source='user.avatar_path', read_only=True)
    userState = serializers.SerializerMethodField()

    class Meta:
        model = TournamentMember
        fields = ['userId', 'username', 'userAvatar', 'userState']

    def get_userState(self, obj):
        if not obj.accepted:
            return 'pending'
        return 'accepted'
