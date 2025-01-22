from rest_framework import serializers
from .models import TournamentMember
from game.models import Game, GameMember

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

class TournamentGamePlayerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatarPath = serializers.CharField(source='user.avatar_path', read_only=True)

    class Meta:
        model = GameMember
        fields = ['id', 'username', 'avatarPath', 'points', 'result']

class TournamentGameSerializer(serializers.ModelSerializer):
    gameId = serializers.IntegerField(source='id', read_only=True)
    mapNumber = serializers.IntegerField(source='map_number', read_only=True)
    state = serializers.CharField(read_only=True)
    finishTime = serializers.DateTimeField(source='finish_time', read_only=True)
    player1 = serializers.SerializerMethodField()
    player2 = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['gameId', 'mapNumber', 'state', 'finishTime', 'deadline', 'player1', 'player2']

    def get_player1(self, obj):
        # Get the first palyer of the game
        game_member = GameMember.objects.filter(game_id=obj.id).order_by('id').first()
        return TournamentGamePlayerSerializer(game_member).data

    def get_player2(self, obj):
        # Get the second player of the game
        game_member = GameMember.objects.filter(game_id=obj.id).order_by('id').last()
        return TournamentGamePlayerSerializer(game_member).data
