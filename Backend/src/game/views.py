# Basic
import logging
from rest_framework import status
# Django
from django.utils.translation import gettext as _
from django.db.models import Case, When, Value, IntegerField
# Core
from core.authentication import BaseAuthenticatedView
from core.response import success_response, error_response
from core.decorators import barely_handle_exceptions
# User
from user.models import User
from user.utils import get_user_by_id
from user.utils_relationship import is_blocking
# Game
from game.models import Game, GameMember
from game.serializer import GameSerializer
from game.utils import create_game, delete_or_quit_game, get_game_of_user

class CreateGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def post(self, request):
        # Get the user from the request
        user = request.user
        opponent_id = request.data.get('opponentId')
        map_number = request.data.get('mapNumber')
        powerups = request.data.get('powerups', False)
        if not opponent_id or not map_number:
            return error_response(_('Missing one of the required fields: opponentId, mapNumber'))
        game, success = create_game(user, opponent_id, map_number, powerups)
        if success:
            return success_response(_('Game created successfully'), **{'gameId': game.id})
        return success_response(_('Game already exists'), **{'gameId': game.id})

class GetGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, userid):
        """
        This endpoint should be called by the frontend before the user want's
        to create a new game. If this call returns a game id, the user will be
        redirected to the game page. If not, the frontend will show the "Create
        Game" Modal.
        """
        user = request.user
        opponent = get_user_by_id(userid)
        game = get_game_of_user(user, opponent)
        if game:
            return success_response(_('Game found'), **{'gameId': game.id})
        return success_response(_('No game found'), **{'gameId': None})

class DeleteGameView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def delete(self, request, id):
        success = delete_or_quit_game(request.user.id, id)
        if success:
            return success_response(_('Game deleted/quit successfully'))
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
        member1 = GameMember.objects.filter(game=game).first()
        member2 = GameMember.objects.filter(game=game).exclude(user=member1.user).first()
        if not member1 or not member2:
            return error_response(_("Game members not found"))
        client_is_player = False
        if member1.user.id == user.id or member2.user.id == user.id:
            client_is_player = True
        tournament_name = None
        if (game.tournament):
            tournament_name = game.tournament.name
        # User with lower id will be playerRight
        if member1.user.id < member2.user.id:
            memberLeft = member2
            memberRight = member1
        else:
            memberLeft = member1
            memberRight = member2
        response_message = {
            'playerLeft':{
                'userId': memberLeft.user.id,
                'username': memberLeft.user.username,
                'avatar': memberLeft.user.avatar,
                'points': memberLeft.points,
                'result': memberLeft.result,
                'ready': game.get_player_ready(memberLeft.user.id),
            },
            'playerRight':{
                'userId': memberRight.user.id,
                'username': memberRight.user.username,
                'avatar': memberRight.user.avatar,
                'points': memberRight.points,
                'result': memberRight.result,
                'ready': game.get_player_ready(memberRight.user.id),
            },
            'gameData': {
                'state': game.state,
                'mapNumber': game.map_number,
                'tournamentId': game.tournament_id,
                'tournamentName': tournament_name,
                'clientIsPlayer': client_is_player,
                'deadline': game.deadline,
            },
        }
        return success_response(_('Lobby details'), **response_message)
        # The frontend will use this response to show the lobby details and
        # establish the WebSocket connection for this specific game

class HistoryView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def get(self, request, userid):
        requester = request.user
        try:
            target = User.objects.get(id=userid)
        except User.DoesNotExist:
            return error_response(_("User not found"), status_code=status.HTTP_404_NOT_FOUND)
        # Check if user is blocked:
        if is_blocking(target, requester):
            return error_response(_("You are blocked by this user"), status_code=status.HTTP_403_FORBIDDEN)

        # Get all games and sort them descending by finish_time
        # Not finsihed games always need to be at the end
        games = Game.objects.filter(
            members__user=target
        ).exclude(
            state=Game.GameState.PENDING
        ).annotate(
            state_order=Case(
                When(state__in=[Game.GameState.ONGOING, Game.GameState.COUNTDOWN], then=Value(1)),
                When(state=Game.GameState.PAUSED, then=Value(2)),
                When(state__in=[Game.GameState.FINISHED, Game.GameState.QUITED], then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by(
            'state_order',
            '-finish_time'
        )
        serializer_games = GameSerializer(games, many=True)
        return success_response(_("Game History fetched"), **{
            'games': serializer_games.data,
        })

class PlayAgainView(BaseAuthenticatedView):
    @barely_handle_exceptions
    def put(self, request, id):
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
        # Game can't be a tournament game
        if old_game.tournament:
            return error_response(_('Tournament games can not be played again'))
        # Game needs to be finished or quited
        logging.info(f"Game state: {old_game.state}")
        if not (old_game.state == Game.GameState.FINISHED or old_game.state == Game.GameState.QUITED):
            return success_response(_('Game is not finished yet!'), **{'gameId': old_game.id})
        opponent_id = GameMember.objects.filter(game=old_game).exclude(user=user).first().user.id
        game, success = create_game(user, opponent_id, old_game.map_number, old_game.powerups)
        if success:
            return success_response(_('Game created successfully'), **{'gameId': game.id})
        return success_response(_('Game already exists'), **{'gameId': game.id})
