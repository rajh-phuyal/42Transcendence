from rest_framework import serializers
from .models import TournamentMember
from game.models import Game

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

class TournamentGameSerializer(serializers.ModelSerializer):
    gameId = serializers.IntegerField(source='id', read_only=True)
    mapNumber = serializers.IntegerField(source='map_number', read_only=True)
    state = serializers.CharField(read_only=True)
    finishTime = serializers.DateTimeField(source='finish_time', read_only=True)

    class Meta:
        model = Game
        fields = ['gameId', 'mapNumber', 'powerups', 'state', 'deadline', 'finishTime']