# Django
from django.utils.translation import gettext as _
# Core
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.decorators import barely_handle_exceptions
# User
from user.models import User
# Game
from game.models import Game, GameMember
from game.utils import create_game, delete_game

class CreateGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        # Get the user from the request
        user = request.user
        powerups = request.data.get('powerups')
        local_game = request.data.get('localGame')
        opponent_id = request.data.get('opponentId')
        map_number = request.data.get('mapNumber')
        game_id, success = create_game(user, opponent_id, map_number, powerups, local_game)
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

class LobbyView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, id):
        user = request.user
        try:
            game = Game.objects.get(id=id)
        except Game.DoesNotExist:
            return error_response(_("Game not found"))
        user_member = GameMember.objects.filter(game=game, user=user).first()
        if not user_member:
            return error_response(_("You are not a member of this game"))
        opponent_member = GameMember.objects.filter(game=game).exclude(user=user).first()
        if not opponent_member:
            return error_response(_("Opponent not found"))
        # Removed this since u can see a lobby even if the game is finished
        #if game.state not in [Game.GameState.PENDING, Game.GameState.ONGOING, Game.GameState.PAUSED]:
        #    return error_response(_("Game can't be played since it's either finished or quited"))

        # TODO: ISSUE #312
        # Check if the game is local, than only the admin can fetch the lobby
        if user_member.local_game and not user_member.admin:
            return error_response(_("Only the admin @{admin_username} can fetch the lobby for local games. You have to go to his computer and play there together")
                .format(admin_username=opponent_member.user.username))

        tournament_name = None
        if (game.tournament):
            tournament_name = game.tournament.name
        # User with lower id will be playerRight
        if user.id < opponent_member.user.id:
            playerLeft = opponent_member.user
            memberLeft = opponent_member
            playerRight = user
            memberRight = user_member
        else:
            playerLeft = user
            memberLeft = user_member
            playerRight = opponent_member.user
            memberRight = opponent_member
        response_message = {
            'playerLeft':{
                'userId': playerLeft.id,
                'username': playerLeft.username,
                'avatar': playerLeft.avatar_path,
                'points': memberLeft.points,
                'ready': game.get_player_ready(playerLeft.id),
            },
            'playerRight':{
                'userId': playerRight.id,
                'username': playerRight.username,
                'avatar': playerRight.avatar_path,
                'points': memberRight.points,
                'ready': game.get_player_ready(playerRight.id),
            },
            'gameData': {
                'state': game.state,
                'mapNumber': game.map_number,
                'tournamentId': game.tournament_id,
                'tournamentName': tournament_name
            },
        }
        return success_response(_('Lobby details'), **response_message)
        # The frontend will use this response to show the lobby details and
        # establish the WebSocket connection for this specific game

class PlayAgainView(BaseAuthenticatedView):
    # TODO:
    @barely_handle_exceptions
    def post(self, request, id):
        """
        This endpoint will be linked to a "Play Again" button in the frontend.
        The first user to click the button will create a new game with the same
        settings as the previous game. The other user will be notified about the
        new game via chat. If the second user clicks the "Play Again" button
        this endpoint will be called again and just return the game id.
        """
        # Get the user from the request
        user = request.user
        old_game = Game.objects.get(id=id)
        # User nedds to be a member of the game
        try:
            GameMember.objects.get(game=old_game, user=user)
        except GameMember.DoesNotExist:
            return error_response(_('You are not a member of this game'))
        # Game needs to be finished or quited
        if not old_game.state == Game.GameState.FINISHED or old_game.state == Game.GameState.QUITED:
            return success_response(_('Game is not finished yet!'), **{'gameId': old_game.id})
        # Game can't be a tournament game
        if old_game.tournament:
            return error_response(_('Tournament games can not be played again'))
        opponent_id = GameMember.objects.filter(game=old_game).exclude(user=user).first().user.id
        local_game = GameMember.objects.filter(game=old_game, user=user).first().local_game
        game_id, success = create_game(user, opponent_id, old_game.map_number, old_game.powerups, local_game)
        if success:
            return success_response(_('Game created successfully'), **{'gameId': game_id})
        return success_response(_('Game already exists'), **{'gameId': game_id})
