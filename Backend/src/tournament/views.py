# Basics
import logging
from rest_framework import status
# Django
from django.db import transaction
from django.utils.translation import gettext as _
from django.db import models
from asgiref.sync import async_to_sync
# Core
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.decorators import barely_handle_exceptions
from core.exceptions import BarelyAnException
# User
from user.models import User
from user.utils_relationship import is_blocking
# Services
from services.constants import PRE_GROUP_TOURNAMENT
from services.send_ws_msg import send_ws_tournament_pm
from services.channel_groups import update_client_in_group
# Game
from game.models import Game, GameMember
from game.serializer import GameSerializer
# Tournament
from tournament.models import Tournament, TournamentMember
from tournament.serializer import TournamentMemberSerializer, TournamentInfoSerializer
from tournament.utils import create_tournament, delete_tournament, join_tournament, leave_tournament, start_tournament

# Checks if user has an active tournament
class EnrolmentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        try:
            # Check if user has an active tournament
            tournament = TournamentMember.objects.get(user_id=user.id, tournament__state=Tournament.TournamentState.ONGOING).tournament
            return success_response(_("User has an active tournament"), **{'tournamentId': tournament.id, 'tournamentName': tournament.name})
        except Exception as e:
            ...  # Continue to the next check
        try:
            # Check if user has an accepted tournament which is not ongoing
            tournament = TournamentMember.objects.get(user_id=user.id, tournament__state=Tournament.TournamentState.SETUP, accepted=True).tournament
            return success_response(_("User has an active tournament"), **{'tournamentId': tournament.id, 'tournamentName': tournament.name})
        except Exception as e:
            return success_response(_("User has no active tournament"), **{'tournamentId': None, 'tournamentName': None})

# History of tournaments of user including all tournament states
class HistoryView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, userid):
        requester = request.user
        try:
            target = User.objects.get(id=userid)
        except User.DoesNotExist:
            return error_response(_("User not found"), status_code=status.HTTP_404_NOT_FOUND)
        # Check if the requester is blocked by the target user
        if is_blocking(target, requester):
            return error_response(_("You are blocked by this user"), status_code=status.HTTP_403_FORBIDDEN)

        # Get all tournaments of the target user
        tournaments = Tournament.objects.filter(
            members__user=target,
            state__in=[Tournament.TournamentState.ONGOING, Tournament.TournamentState.FINISHED]
        ).order_by(
            'state',
            '-finish_time'
        )

        # Serialize the tournaments using TournamentInfoSerializer
        serializer_tournaments = TournamentInfoSerializer(tournaments, many=True)

        return success_response(_("Tournament history fetched successfully"), **{
            'tournaments': serializer_tournaments.data
        })

# All tournaments where user is invited to and public tournaments
class ToJoinView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        # Get all tournaments where user is invited to
        invited_tournaments = TournamentMember.objects.filter(
            user_id=user.id,
            accepted=False,
            tournament__state=Tournament.TournamentState.SETUP
        ).values_list('tournament', flat=True)
        public_tournaments = Tournament.objects.filter(
            public_tournament=True,
            state=Tournament.TournamentState.SETUP
        )
        # Merge the two querysets
        tournaments = list(invited_tournaments) + list(public_tournaments)
        tournamentsSerializer = TournamentInfoSerializer(tournaments, many=True)
        return success_response(_("Returning the tournaments which are available for the user"), **{'tournaments': tournamentsSerializer.data})

class CreateTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        logging.info(f"Request data: {request.data}")
        # Get the user from the request
        user = request.user
        tournament_name = request.data.get('name').strip()
        tournament = create_tournament(
            creator_id=user.id,
            name=tournament_name,
            local_tournament=request.data.get('local'),
            public_tournament=request.data.get('public'),
            map_number=request.data.get('mapNumber'),
            powerups=request.data.get('powerups'),
            opponent_ids=request.data.get('opponentIds')
        )

        if not tournament.public_tournament:
            send_ws_tournament_pm(tournament.id, f"**TI,{user.id},<userid>,{tournament.as_clickable()}**")

        return success_response(_("Tournament created successfully"), **{'tournamentId': tournament.id})

class DeleteTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request, id):
        user = request.user
        delete_tournament(user, id)
        return success_response(_("Tournament deleted successfully"))
class JoinTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request, id):
        user = request.user
        join_tournament(user, id)
        return success_response(_("Tournament joined successfully"))

class LeaveTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request, id):
        user = request.user
        leave_tournament(user, id)
        return success_response(_("Tournament left successfully"))

class StartTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request, id):
        user = request.user
        start_tournament(user, id)
        return success_response(_("Tournament started successfully"))

class TournamentLobbyView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, id):
        user = request.user
        tournament = Tournament.objects.filter(id=id).first()
        if not tournament:
            return error_response(_("Tournament not found"), status_code=status.HTTP_404_NOT_FOUND)
        # Add client to websocket group if tournament is not finished
        if tournament.state != Tournament.TournamentState.FINISHED:
            async_to_sync(update_client_in_group)(user, tournament.id, PRE_GROUP_TOURNAMENT, add=True)
        # Define the client role:
        role = ""
        try:
            tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament.id)
            if tournament_member.is_admin:
                role = "admin"
            else:
                if tournament_member.accepted:
                    role = "member"
                else:
                    role = "invited"
        except TournamentMember.DoesNotExist:
            role = "fan"
        # Serialize the tournament info
        serializer_info = TournamentInfoSerializer(tournament)
        # Serialize the tournament members
        tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
        serializer_members = TournamentMemberSerializer(tournament_members, many=True)
        # Serialize the tournament games
        games = Game.objects.filter(tournament_id=tournament.id)
        serializer_games = GameSerializer(games, many=True)

        # Send all data at once to the frontend
        return success_response(_("Tournament lobby fetched successfully"), **{
            'clientRole': role,
            'tournamentInfo': serializer_info.data,
            'tournamentMembers': serializer_members.data,
            'tournamentGames': serializer_games.data,
        })

# If the user is in a tournament and has a pending game with a deadline set,
# this endpoint will return the gameId so that the FE can redir to the game
# lobby page. In any other case this endpoint will return an error_response
class GoToGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        tournament_id=request.data.get('tournamentId')
        if not tournament_id:
            return error_response(_("tournament_id is required"))
        tournament = Tournament.objects.get(id=tournament_id)
        # Check if user is in the tournament
        try:
            tournament_member = TournamentMember.objects.get(user_id=user.id, tournament_id=tournament_id)
        except TournamentMember.DoesNotExist:
            return error_response(_("U are not part of the tournament"), status_code=status.HTTP_403_FORBIDDEN)
        # Check if the tournament is ongoing
        if tournament.state != Tournament.TournamentState.ONGOING:
            return error_response(_("Tournament is not ongoing"))
        # Get the game wich needs to be pending or paused and has a deadline set
        sheduelted_games = Game.objects.filter(
            tournament_id=tournament_id,
            state__in=[Game.GameState.PENDING, Game.GameState.PAUSED],
            deadline__isnull=False)
        if not sheduelted_games:
            return error_response(_("No pending games with deadline set found"))
        # Filter the sheduelted games to get the game that the user is part of
        try:
            game_member_entry = GameMember.objects.filter(
                user_id=user.id,
                game__in=sheduelted_games)
            return success_response(_("Shedueled Game found"), **{'gameId': game_member_entry.first().game_id})
        except GameMember.DoesNotExist:
            return error_response(_("The overloards ask u to be patient. There will be a game for u soon."))
