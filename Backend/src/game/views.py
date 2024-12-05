from core.base_views import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
from user.utils_relationship import is_blocking, are_friends
from user.constants import USER_ID_AI
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
        opponent_id = request.data.get('opponent')
        if not opponent_id:
            return error_response(_("Missing key 'opponent'"))
        # Check if opponent exist
        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            return error_response(_('Opponent not found'))
        # Check if opponent isn't urself, is ur friend and not blocking you
        if opponent == user:
            return error_response(_("You can't play against yourself"))
        if not are_friends(user, opponent):
            return error_response(_("You can only play against your friends"))
        if is_blocking(opponent, user):
            return error_response(_("You are blocked by this user"))
        # Check if opponent is AI
        if opponent.id == USER_ID_AI:
            # TODO: issue #210
            return error_response(_("Not implemented yet"))
        # Check if there is already a direct game between the user and the opponent
        user_games = GameMember.objects.filter(
            user=user.id,
            game__tournament_id=None,
            game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
        ).values_list('game_id', flat=True)
        opponent_games = GameMember.objects.filter(
            user=opponent.id,
            game__tournament_id=None,
            game__state__in=[Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]
        ).values_list('game_id', flat=True)
        if user_games or opponent_games:
            common_games = set(user_games).intersection(opponent_games)
            if common_games:
                game_id = common_games.pop()
                return success_response(_('Game already exists'), **{'game_id': game_id})

        # Create the game and the game members in a transaction
        with transaction.atomic():
            game = Game.objects.create(
                map_number=map_number,
                powerups=powerups,
            )
            game_member_user = GameMember.objects.create(
                game=game,
                user=user,
                local_game=local_game,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups
            )
            game_member_opponent = GameMember.objects.create(
                game=game,
                user=opponent,
                local_game=local_game,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups
            )
            game.save()
            game_member_user.save()
            game_member_opponent.save()

        return success_response(_('Game created successfully'), **{'game_id': game.id})