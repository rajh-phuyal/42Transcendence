from core.base_views import BaseAuthenticatedView
from django.db import transaction
from core.response import success_response, error_response
from user.models import User
from game.models import Game, GameMember
from django.utils.translation import gettext as _
from core.decorators import barely_handle_exceptions
# from django.db.models import Q

class CreateGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        # Get the user from the request
        user = request.user
        map_number = request.data.get('map_number')
        if not map_number in [0, 1, 2, 3, 4]:
            return error_response(_("Invalid value for key 'map_number'"))
        powerups = request.data.get('powerups')
        if not powerups in ['true', 'false']:
            return error_response(_("Invalid value for key 'powerups' (must be 'true' or 'false')"))
        if powerups == 'true':
            powerups = True
        else:
            powerups = False
        opponent_id = request.data.get('opponent')
        if not opponent_id:
            return error_response(_("Missing key 'opponent'"))
        opponent = User.objects.filter(id=opponent_id).first()
        if opponent == user:
            return error_response(_("You can't play against yourself"))
        if not opponent:
            return error_response(_('Opponent not found'))

        # Check if there is already a game between the user and the opponent
        # TODO: issue #185 (https://github.com/rajh-phuyal/42Transcendence/issues/185)
        #current_game = Game.objects.filter(
        #    game_members__user=user,  # Use 'game_members' because it's the related name for GameMember in User
        #    game_members__user=opponent,
        #    tournament_id__isnull=True,
        #    state__ne=Game.GameState.FINISHED
        #).first()
        #if current_game:
        #    logging.info(f'User {user.id} is already in a game with opponent {opponent.id}, game_id: {current_game.id}')
        #    return error_response(_('You already have a game with this opponent'), **{'game_id': current_game.id})

        with transaction.atomic():
            game = Game.objects.create(
                map_number=map_number,
                powerups=powerups,
            )
            game_member_user = GameMember.objects.create(
                game=game,
                user=user,
                local_game=False,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups
            )
            game_member_opponent = GameMember.objects.create(
                game=game,
                user=opponent,
                local_game=False,
                powerup_big = powerups,
                powerup_fast = powerups,
                powerup_slow = powerups
            )
            game.save()
            game_member_user.save()
            game_member_opponent.save()

        return success_response(_('Game created successfully'), **{'game_id': game.id})

class DeleteGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request):
        error_response('Not implemented yet')
