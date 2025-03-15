from rest_framework import serializers
from .models import TournamentMember, Tournament
from game.models import Game, GameMember

class TournamentInfoSerializer(serializers.ModelSerializer):
    adminId = serializers.SerializerMethodField()
    adminName = serializers.SerializerMethodField()
    mapNumber = serializers.IntegerField(source='map_number', read_only=True)
    public = serializers.BooleanField(source='public_tournament', read_only=True)
    local = serializers.BooleanField(source='local_tournament', read_only=True)
    finishTime = serializers.DateTimeField(source='finish_time', read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'adminId', 'adminName', 'state', 'mapNumber', 'powerups', 'public', 'local', 'finishTime']

    def get_adminId(self, obj):
        return obj.members.filter(is_admin=True).first().user.id

    def get_adminName(self, obj):
        return obj.members.filter(is_admin=True).first().user.username

class TournamentMemberSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatarUrl = serializers.CharField(source='user.avatar_path', read_only=True)
    state = serializers.SerializerMethodField()
    playedGames = serializers.IntegerField(source='played_games', read_only=True)
    wonGames = serializers.IntegerField(source='won_games', read_only=True)
    winPoints = serializers.IntegerField(source='win_points', read_only=True)
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = TournamentMember
        fields = ['id', 'username', 'avatarUrl', 'state', 'playedGames', 'wonGames', 'winPoints', 'rank']

    def get_state(self, obj):
        if not obj.accepted:
            return 'pending'
        return 'accepted'
