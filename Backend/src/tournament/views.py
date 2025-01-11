from core.authentication import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from tournament.models import Tournament, TournamentMember, TournamentState
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from tournament.utils import create_tournament, delete_tournament, join_tournament, leave_tournament, start_tournament
from core.exceptions import BarelyAnException
from tournament.serializer import TournamentMemberSerializer, TournamentGameSerializer
import logging
from django.db import models
from tournament.utils_ws import join_tournament_channel, send_tournament_invites_via_pm, send_tournament_invites_via_ws

# Checks if user has an active tournament
class EnrolmentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        try:
            # Check if user has an active tournament
            tournament = TournamentMember.objects.get(user_id=user.id, tournament__state=TournamentState.ONGOING).tournament
            return success_response(_("User has an active tournament"), **{'tournamentId': tournament.id, 'tournamentName': tournament.name})
        except Exception as e:
            ...  # Continue to the next check
        try:
            # Check if user has an accepted tournament which is not ongoing
            tournament = TournamentMember.objects.get(user_id=user.id, tournament__state=TournamentState.SETUP, accepted=True).tournament
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
            tournament__state=TournamentState.SETUP
        ).annotate(
            tournamentId=models.F('tournament_id'),
            tournamentName=models.F('tournament__name')
        ).values(
            'tournamentId',
            'tournamentName'
        )
        public_tournaments = Tournament.objects.filter(
            public_tournament=True,
            state=TournamentState.SETUP
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
    # @barely_handle_exceptions TODO: HACKATHON uncomment this line
    def post(self, request):
        # Get the user from the request
        user = request.user
        tournament = create_tournament(
            creator_id=user.id,
            name=request.data.get('name'),
            local_tournament=request.data.get('localTournament'),
            public_tournament=request.data.get('publicTournament'),
            map_number=request.data.get('mapNumber'),
            powerups_string=request.data.get('powerups'),
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
        role = ""
        tournament = Tournament.objects.get(id=id)
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

        # Get all members of the tournament and serialize them
        tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
        admin_name = tournament_members.get(is_admin=True).user.username
        tournament_members_data = TournamentMemberSerializer(tournament_members, many=True).data
        # Get all games of the tournament and serialize them
        games = Game.objects.filter(tournament_id=tournament.id)
        games_data = TournamentGameSerializer(games, many=True).data

        # Get details of the tournament
        response_json = {
            'tournamentId': tournament.id,
            'tournamentName': tournament.name,
            'createdBy': admin_name,
            'tournamentState': tournament.state,
            'tournamentMapNumber': tournament.map_number,
            'tournamentPowerups': tournament.powerups,
            'tournamentPublic': tournament.public_tournament,
            'tournamentLocal': tournament.local_tournament,
            'clientRole': role,
            'tournamentMembers': tournament_members_data,
            'tournamentGames': games_data
        }

        # Add client to websocket group if game is not finished
        if tournament.state != TournamentState.FINISHED:
            join_tournament_channel(user, tournament.id)
        return success_response(_("Tournament lobby fetched successfully"), **response_json)