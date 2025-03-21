from rest_framework import serializers
from game.models import Game, GameMember

class GamePlayerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = GameMember
        fields = ['id', 'username', 'avatar', 'points', 'result']

class GameSerializer(serializers.ModelSerializer):
    # TODO: ISSUE #193
    finishTime = serializers.DateTimeField(source='finish_time', read_only=True)
    # TODO: ISSUE #193
    #deadline = serializers.DateTimeField(source='deadline', read_only=True)
    playerLeft = serializers.SerializerMethodField()
    playerRight = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ['id', 'state', 'type', 'deadline', 'finishTime', 'playerLeft', 'playerRight']

    def get_playerLeft(self, obj):
        game_member = GameMember.objects.filter(game_id=obj.id).order_by('id').last()
        if game_member is None:
            return None
        return GamePlayerSerializer(game_member).data

    def get_playerRight(self, obj):
        game_member = GameMember.objects.filter(game_id=obj.id).order_by('id').first()
        if game_member is None:
            return None
        return GamePlayerSerializer(game_member).data
