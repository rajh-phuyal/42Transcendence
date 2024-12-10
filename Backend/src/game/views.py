from core.base_views import BaseAuthenticatedView
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from game.utils import create_game, delete_game
# from django.db.models import Q

class CreateGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        # Get the user from the request
        user = request.user
        # Parse the input
        map_number = request.data.get('mapNumber')
        if not map_number in [1, 2, 3, 4]:
            return error_response(_("Invalid value for key 'mapNumber' value (must be 1, 2, 3 or 4)"))
        powerups = request.data.get('powerups')
        if not powerups in ['true', 'false']:
            return error_response(_("Invalid value for key 'powerups' (must be 'true' or 'false')"))
        if powerups == 'true':
            powerups = True
        else:
            powerups = False
        local_game = request.data.get('localGame')
        if not local_game in ['true', 'false']:
            return error_response(_("Invalid value for key 'localGame' (must be 'true' or 'false')"))
        if local_game == 'true':
            local_game = True
        else:
            local_game = False
        if local_game:
            # TODO: issue #211
            return error_response(_("Local games are not supported yet"))
        opponent_id = request.data.get('opponentId')
        if not opponent_id:
            return error_response(_("Missing key 'opponentId'"))
                    
        game_id, success = create_game(user.id, opponent_id, map_number, powerups, local_game)
        if success:
            return success_response(_('Game created successfully'), **{'gameId': game_id})
        return success_response(_('Game already exists'), **{'gameId': game_id})

class DeleteGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request, id):
        success = delete_game(request.user.id, id)
        if success:
            return success_response(_('Game deleted successfully'))
        # Most likely this won't be reached since delete_game will raise an
        # exception in error cases
        return error_response(_('Could not delete game'))
