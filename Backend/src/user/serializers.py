from django.db.models import Q
from user.models import User, IsCoolWith
from rest_framework import serializers
from user.utils_relationship import get_relationship_status
from django.core.cache import cache
from chat.models import Conversation
from game.models import GameMember
from tournament.models import TournamentMember
from django.db.models import Count, Subquery, Sum, IntegerField
from django.db.models.functions import Coalesce
from user.constants import NORM_STATS_SKILL, NORM_STATS_GAME_EXP, NORM_STATS_TOURNAMENT_EXP
import logging

class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_path']

# This will prepare the data for endpoint '/user/profile/<int:id>/'
class ProfileSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.CharField(source='avatar_path')
    firstName = serializers.CharField(source='first_name', default="John")
    lastName = serializers.CharField(source='last_name', default="Doe")
    online = serializers.SerializerMethodField()
    lastLogin = serializers.SerializerMethodField()
    chatId = serializers.SerializerMethodField()
    newMessage = serializers.BooleanField(default=True)
    relationship = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatarUrl', 'firstName', 'lastName', 'online', 'lastLogin', 'language', 'chatId', 'newMessage', 'relationship', 'stats']

    def get_lastLogin(self, obj):
        # Check if `last_login` is None or `online` is True
        if obj.last_login is None or self.get_online(obj):
            return "under surveillance"

        # Otherwise, format `last_login` as 'YYYY-MM-DD hh:mm'
        return obj.last_login.strftime("%Y-%m-%d %H:%M") #TODO: Issue #193

    def get_online(self, user):
        # Check if the user's online status is in the cache
        return user.get_online_status()

    # Valid types are 'yourself' 'noFriend', 'friend', 'requestSent', 'requestReceived'
    def get_relationship(self, obj):
        # `requester` is the current authenticated user
        requester = self.context['request'].user
        # `requested` is the user object being serialized (from the URL)
        requested = obj
        return get_relationship_status(requester, requested)

    def get_stats(self, obj):
        current_user = self.context['request'].user

        # Fetching total games and games won
        total_games = GameMember.objects.filter(user=current_user).count()
        games_won = GameMember.objects.filter(user=current_user, result='won').count()

        # Fetching the top user's total games
        top_user_total_games = (
            User.objects
            .annotate(total_games=Count('game_members'))
            .order_by('-total_games')
            .values_list('total_games', flat=True)
            .first() or 1  # Default to 1 to prevent division errors
        )

        # Fetching tournament stats
        total_tournament_games = (
            TournamentMember.objects.filter(user=current_user)
            .aggregate(total_games=Sum('played_games'))['total_games'] or 0
        )

        top_tournament_total_games = (
            User.objects
            .annotate(total_games=Sum('tournament_members__played_games'))
            .order_by('-total_games')
            .values_list('total_games', flat=True)
            .first() or 1  # Default to 1 to prevent division errors
        )

        # Raw skill and experience calculations
        skill = (games_won or 0) / (total_games or 1)
        game_experience = (total_games or 1) / (top_user_total_games or 1)
        tournament_experience = (total_tournament_games or 1) / (top_tournament_total_games or 1)

        # Normalize values into 0-100% range (clamping max at 100%)
        def normalize(value):
            return min(round(value * 100, 2), 100)  # Convert to percentage, max 100%

        skill_norm = normalize(skill)
        game_experience_norm = normalize(game_experience)
        tournament_experience_norm = normalize(tournament_experience)

        # Normalize total score into 0-100 range based on weight factors
        total_score = (
            NORM_STATS_SKILL * skill +
            NORM_STATS_GAME_EXP * game_experience +
            NORM_STATS_TOURNAMENT_EXP * tournament_experience
        )
        total_score_norm = min(round(total_score, 2), 100)

        return {
            "game": {
                "won": games_won,
                "played": total_games
            },
            "tournament": {
                "firstPlace": 5, 
                "secondPlace": 6,
                "thirdPlace": 7, 
                "played": total_tournament_games
            },
            "score": {
                "skill": skill_norm,
                "experience": game_experience_norm,
                "performance": tournament_experience_norm,
                "total": total_score_norm
            }
        }

    def get_chatId(self, obj):
        # `requester` is the current authenticated user
        requester = self.context['request'].user
        # `requested` is the user object being serialized (from the URL)
        requested = obj
        # Check if the requester and requested are in the same conversation
        conversation_id = Conversation.objects.filter(
            is_group_conversation=False,
            members__user=requester
        ).filter(members__user=requested
        ).values_list('id', flat=True).first()
        return conversation_id

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
        user_id = self.context.get('target_user_id')
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
        # TODO: Friendship status should be from the perspective of the requester
        # 'requester_user_id'
        # 'target_user_id'
        user_id = self.context.get('requester_user_id')
        if obj.status == IsCoolWith.CoolStatus.PENDING:
            return 'requestSent' if obj.requester.id == user_id else 'requestReceived'
        return 'friend'
