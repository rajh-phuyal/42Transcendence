from core.base_views import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from tournament.utils import create_tournament
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
        return success_response(_("Tournament created successfully"), **{'tournamentId': tournament.id})