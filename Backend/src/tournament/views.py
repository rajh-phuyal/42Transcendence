from core.authentication import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from tournament.models import Tournament, TournamentMember
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from tournament.utils import create_tournament, delete_tournament, join_tournament, leave_tournament, prepare_tournament_data_json, start_tournament
from core.exceptions import BarelyAnException
from tournament.serializer import TournamentMemberSerializer, TournamentGameSerializer, TournamentRankSerializer
import logging
from django.db import models
from tournament.utils_ws import join_tournament_channel, send_tournament_invites_via_pm, send_tournament_invites_via_ws
from rest_framework import status
import re

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
    def get(self, request):
        user = request.user
        # Get all tournaments of the user
        tournaments = TournamentMember.objects.filter(
            user_id=user.id
        ).annotate(
            tournamentId=models.F('tournament_id'),
            tournamentName=models.F('tournament__name'),
            tournamentState=models.F('tournament__state')
        ).values(
            'tournamentId',
            'tournamentName',
            'tournamentState'
        )
        return success_response(_("User's tournament history fetched successfully"), **{'tournaments': tournaments})

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
        ).annotate(
            tournamentId=models.F('tournament_id'),
            tournamentName=models.F('tournament__name')
        ).values(
            'tournamentId',
            'tournamentName'
        )
        public_tournaments = Tournament.objects.filter(
            public_tournament=True,
            state=Tournament.TournamentState.SETUP
        ).annotate(
            tournamentId=models.F('id'),
            tournamentName=models.F('name')
        ).values(
            'tournamentId',
            'tournamentName'
        )
        # Merge the two querysets
        tournaments = list(invited_tournaments) + list(public_tournaments)
        return success_response(_("Returning the tournaments which are available for the user"), **{'tournaments': tournaments})

class CreateTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        logging.info(f"Request data: {request.data}")
        # Get the user from the request
        user = request.user
        tournament_name = request.data.get('name')

        # Check if tournament name is not empty
        if not tournament_name:
            raise BarelyAnException(_("Tournament name cannot be empty"))

        # Validate tournament name using regex
        if not re.match(r'^[a-zA-Z0-9\-_]+$', tournament_name):
            raise BarelyAnException(_("Tournament name can only contain letters, numbers, hyphens (-), and underscores (_)"))

        tournament = create_tournament(
            creator_id=user.id,
            name=tournament_name,
            local_tournament=request.data.get('localTournament'),
            public_tournament=request.data.get('publicTournament'),
            map_number=request.data.get('mapNumber'),
            powerups=request.data.get('powerups'),
            opponent_ids=request.data.get('opponentIds')
        )

        if not tournament.public_tournament:
            send_tournament_invites_via_ws(tournament.id)
            send_tournament_invites_via_pm(tournament.id)

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

        tournament = Tournament.objects.get(id=id)

        # Add client to websocket group if tournament is not finished
        if tournament.state != Tournament.TournamentState.FINISHED:
            join_tournament_channel(user, tournament.id)

        response_json=prepare_tournament_data_json(user, tournament)
        return success_response(_("Tournament lobby fetched successfully"), **response_json)

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
