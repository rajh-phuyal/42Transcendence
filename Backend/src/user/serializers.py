from django.db.models import Q
from user.models import User, IsCoolWith
from rest_framework import serializers
from user.utils_relationship import get_relationship_status
from django.core.cache import cache
from chat.models import Conversation
from game.models import GameMember
from tournament.models import TournamentMember, Tournament
from game.models import GameMember, Game
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
    def get_relationship(self, user):
        # `requester` is the current authenticated user
        requester = self.context['request'].user
        # `requested` is the user object being serialized (from the URL)
        requested = user
        return get_relationship_status(requester, requested)

    def get_stats(self, user):
        # Normalize values into a 0-100% range
        def convertToPercentage(value):
            return round(value * 100, 2)

        # GAMES
        # =====
        total_games_played_objects = GameMember.objects.filter(
            user=user,
            game__state__in=[Game.GameState.FINISHED, Game.GameState.QUITED]
        )
        games_played = total_games_played_objects.count()
        games_won = total_games_played_objects.filter(result = GameMember.GameResult.WON).count()
        skill = (games_won or 0) / (games_played or 1)
        #logging.info(f"GAMES: played / won / skill: {games_played} / {games_won} / {skill}")

        # TOURNAMENTS
        # ===========
        total_tournaments_played_objects=Tournament.objects.filter(
            state=Tournament.TournamentState.FINISHED,
            members__user=user
        )
        tournaments_played = total_tournaments_played_objects.count()
        #logging.info(f"TOURNAMENT: played: {tournaments_played}")

        # This section is to get the rank of the user in the tournament
        tournament_first_place_count=0
        tournament_second_place_count=0
        tournament_third_place_count=0
        for tournament in total_tournaments_played_objects:
            # Get the toutnament games
            tournament_games = Game.objects.filter(tournament=tournament)
            tournament_final_game = tournament_games.filter(type=Game.GameType.FINAL).first()
            if GameMember.objects.filter(
                game=tournament_final_game,
                user=user,
                result=GameMember.GameResult.WON).exists():
                    # Player won this tournment so increment the count
                    tournament_first_place_count += 1
                    continue
            if GameMember.objects.filter(
                game=tournament_final_game,
                user=user,
                result=GameMember.GameResult.LOST).exists():
                    # Player lost the final so -> second place
                    tournament_second_place_count += 1
                    continue
            tournament_semi_final_game = tournament_games.filter(type=Game.GameType.SEMI_FINAL).first()
            if(tournament_semi_final_game):
                # It was a tournament with semi finals aka more than 3 players
                if GameMember.objects.filter(
                    game=tournament_semi_final_game,
                    user=user,
                    result=GameMember.GameResult.WON).exists():
                        # Player won the semi final so -> third place
                        tournament_third_place_count += 1
                        continue
            else:
                # There was no semi final so use the rank for third place
                third_place_user = TournamentMember.objects.filter(
                    tournament=tournament,
                    rank=3
                ).first()
                if third_place_user.user == user:
                    # Player was ranked third
                    tournament_third_place_count += 1
                    continue
        #logging.info(f"TOURNAMENT: 1st / 2nd / 3rd: {tournament_first_place_count} / {tournament_second_place_count} / {tournament_third_place_count}")

        # EXPERIENCE
        # ==========

        # The top user is the user on the app with the most games played
        # Fetch the top user's total games (to compare to the current user)
        top_user_total_games_played_count = (
            User.objects
            .annotate(
                total_games=Count(
                    'games',
                    filter=Q(games__game__state__in=[Game.GameState.FINISHED, Game.GameState.QUITED])
                )
            )
            .order_by('-total_games')
            .values_list('total_games', flat=True)
            .first()
        )
        # Fetch the top player's total tournament games (to compare to the current user))
        top_user_total_tournaments_played_count = (
            User.objects
            .annotate(
                total_tournaments=Count(
                    'tournaments',
                    filter=Q(tournaments__tournament__state=Tournament.TournamentState.FINISHED)
                )
            )
            .order_by('-total_tournaments')
            .values_list('total_tournaments', flat=True)
            .first() or 1  # Prevent division by zero
        )
        #logging.info(f"TOP USER: total games / total tournaments: {top_user_total_games_played_count} / {top_user_total_tournaments_played_count}")

        # Calculate raw experience values for client
        game_experience         = games_played       / (top_user_total_games_played_count       or 1) # 'or 1' => Prevent division by zero
        tournament_experience   = tournaments_played / (top_user_total_tournaments_played_count or 1) # 'or 1' => Prevent division by zero
        #logging.info(f"EXPERIENCE: game / tournament: {game_experience} / {tournament_experience}")

        # Compute total score based on weights
        total_score = (
            NORM_STATS_SKILL * skill +
            NORM_STATS_GAME_EXP * game_experience +
            NORM_STATS_TOURNAMENT_EXP * tournament_experience
        )

        #logging.info(f"EXPERIENCE: skill / game / tournament / total: {skill} / {game_experience} / {tournament_experience} / {total_score}")

        # From 0.1 -> 10%
        skill = convertToPercentage(skill)
        game_experience = convertToPercentage(game_experience)
        tournament_experience = convertToPercentage(tournament_experience)
        total_score = convertToPercentage(total_score)
        #logging.info(f"EXPERIENCE: skill / game / tournament / total: {skill} / {game_experience} / {tournament_experience} / {total_score}")

        return {
            "game": {
                "won": games_won,
                "played": games_played
            },
            "tournament": {
                "firstPlace": tournament_first_place_count,
                "secondPlace": tournament_second_place_count,
                "thirdPlace": tournament_third_place_count,
                "played": tournaments_played
            },
            "score": {
                "skill": skill,
                "experience": game_experience,
                "performance": tournament_experience,
                "total": total_score
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
