from core.authentication import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from tournament.models import Tournament, TournamentMember, TournamentState
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from tournament.utils import create_tournament, get_tournament_and_member, join_tournament
from core.exceptions import BarelyAnException
from tournament.serializer import TournamentMemberSerializer

# Checks if user has an active tournament
class EnrolmentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        try:
            tournament = TournamentMember.objects.get(user_id=user.id, tournament__state=TournamentState.ONGOING).tournament
            return success_response(_("User has an active tournament"), **{'tournamentId': tournament.id, 'tournamentName': tournament.name})
        except Tournament.DoesNotExist:
            return success_response(_("User has no active tournament"), **{'tournamentId': None, 'tournamentName': None})

# History of tournaments of user including all tournament states
class HistoryView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        # Get all tournaments of the user
        tournaments = TournamentMember.objects.filter(user_id=user.id).values('tournament_id', 'tournament__name', 'tournament__state')
        return success_response(_("User's tournament history fetched successfully"), **{'tournaments': tournaments})

# All tournaments where user is invited to and public tournaments
class ToJoinView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request):
        user = request.user
        # Get all tournaments where user is invited to
        invited_tournaments = TournamentMember.objects.filter(user_id=user.id, accepted=False, tournament__state=TournamentState.SETUP).values('tournament_id', 'tournament__name')
        public_tournaments = Tournament.objects.filter(public_tournament=True, state=TournamentState.SETUP).values('id', 'name')
        # Merge the two querysets
        tournaments = list(invited_tournaments) + list(public_tournaments)
        return success_response(_("Returning the tournaments which are available for the user"), **{'tournaments': tournaments})

class CreateTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
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
        # TODO: Send websocket messages to all members via chat
        return success_response(_("Tournament created successfully"), **{'tournamentId': tournament.id})

class DeleteTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request, id):
        user = request.user
        try:
            tournament, tournament_member = get_tournament_and_member(user, id, need_admin=True)
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)

        # Check if the tournament has already started
        if not tournament.state == TournamentState.SETUP:
            return error_response(_("Tournament can only be deleted if it is in setup state"))
        # Delete the tournament
        with transaction.atomic():
            # TODO: Not sure if we can have games and game members while still being in setup state
            tournament_games = Game.objects.filter(tournament_id=tournament.id)
            tournament_game_members = GameMember.objects.filter(game__in=tournament_games)
            # This one needs to be deleted for sure
            tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
            # Delete in reverse order to avoid foreign key constraint errors
            tournament_game_members.delete()
            tournament_games.delete()
            tournament_members.delete()
            tournament.delete()
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
        try:
            tournament, tournament_member = get_tournament_and_member(user, id)
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        # Check if the tournament has already started
        if tournament.state != TournamentState.SETUP:
            return error_response(_("Tournament can only be left if it is in setup state"))
        # Check if the user is the admin of the tournament
        if tournament_member.is_admin:
            return error_response(_("Admin can't leave the tournament. Please delete the tournament instead"))
        # Delete the tournament member
        tournament_member.delete()
        return success_response(_("Tournament left successfully"))
        # TODO: check if there are enough players left and cancel the tournament if not (only for private tournaments)
        # TODO: send websocket update message to admin to update the lobby

class StartTournamentView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request, id):
        user = request.user
        try:
            tournament, tournament_member = get_tournament_and_member(user, id, need_admin=True)
        except BarelyAnException as e:
            return error_response(str(e.detail), e.status_code)
        # Check if the tournament has already started
        if not tournament.state == TournamentState.SETUP:
            return error_response(_("Tournament can only be started if it is in setup state"))
        # Check if at least 3 members are there
        tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id, accepted=True)
        tournament_members_count = tournament_members.count()
        # Check if all members are online
        if not all([tournament_members.user.get_online_status() for tournament_members in tournament_members]):
            return error_response(_("All members must be online to start the tournament"))
        # Start the tournament
        with transaction.atomic():
            tournament.state = 'ongoing'
            tournament.save()
            # Remove all persons who have not accepted the invitation
            TournamentMember.objects.filter(tournament_id=tournament.id, accepted=False).select_for_update().delete()
            # Create the games
            # TODO:
        # TODO: Send websocket update message to all members to start the game
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

        # Get all members of the tournament
        tournament_members = TournamentMember.objects.filter(tournament_id=tournament.id)
        # Serialize the members
        tournament_members_data = TournamentMemberSerializer(tournament_members, many=True).data

        # Get all games of the tournament
        games = Game.objects.filter(tournament_id=tournament.id)

        # Get details of the tournament
        response_json = {
            'tournamentId': tournament.id,
            'tournamentName': tournament.name,
            'createdBy': 'TODO',
            'tournamentState': tournament.state,
            'tournamentMapNumber': tournament.map_number,
            'tournamentPowerups': tournament.powerups,
            'tournamentPublic': tournament.public_tournament,
            'tournamentLocal': tournament.local_tournament,
            'clientRole': role,
            'tournamentMembers': tournament_members_data,
            #'tournamentGames': games
        }
        return success_response(_("Tournament lobby fetched successfully"), **response_json)