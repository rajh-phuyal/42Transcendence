# Basics
import random, logging
from copy import deepcopy
# Django
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.db import transaction
from asgiref.sync import sync_to_async
# Core
from core.exceptions import BarelyAnException
# Game
from game.constants import GAME_STATE, GAME_PLAYER_INPUT, PADDLE_OFFSET
from game.models import Game, GameMember
from game.utils import is_left_player, get_user_of_game, finish_game
from game.game_cache import get_game_data, set_game_data
# Channels
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

@database_sync_to_async
def update_game_state(game_id, state):
    # Update cache
    set_game_data(game_id, 'gameData', 'state', state)
    # Update db
    with transaction.atomic():
        game = Game.objects.select_for_update().get(id=game_id)
        if (state == Game.GameState.FINISHED):
            # Use my finish_game function to deal with everything
            winner, looser = finish_game(game)
            if is_left_player(game_id, winner.user_id):
                set_game_data(game_id, 'playerLeft', 'result', GameMember.GameResult.WON)
                set_game_data(game_id, 'playerRight', 'result', GameMember.GameResult.LOST)
            else:
                set_game_data(game_id, 'playerLeft', 'result', GameMember.GameResult.LOST)
                set_game_data(game_id, 'playerRight', 'result', GameMember.GameResult.WON)
        else:
            game.state = state
            if(state == Game.GameState.ONGOING):
                game.deadline = None # So the recconection deadline is gone
        game.save()

    # TODO: tournament game issue #309
    # if tournament game
    #      inform tournament guys (gameUpdateState)
    logging.info(f"Game state updated (cache and db) to: {state}")

@database_sync_to_async
def update_game_points(game_id, player_id=None, player_side=None):
    # If the player id is not provided, we have to find it by the side
    if player_id is None:
        if player_side is None:
            logging.error("update_game_points: player_id and player_side are None u must provide one")
            return
        player_id = get_user_of_game(game_id, player_side)
        if not player_id:
            logging.error("update_game_points: player_id not found")
            return

    # If player_side is not provided, we have to find it by the player_id
    if player_side is None:
        if is_left_player(game_id, player_id):
            player_side = 'playerLeft'
        else:
            player_side = 'playerRight'

    # Update cache
    set_game_data(game_id, player_side, 'points', get_game_data(game_id, player_side, 'points') + 1)

    # Update db
    with transaction.atomic():
        gameMember = GameMember.objects.select_for_update().get(game_id=game_id, user_id=player_id)
        gameMember.points += 1
        gameMember.save()

    # TODO: tournament game # issue #309
    # if tournament game
    #      inform tournament guys (gameUpdateScore)

    points_left = get_game_data(game_id, 'playerLeft', 'points')
    points_right = get_game_data(game_id, 'playerRight', 'points')
    logging.info(f"Game {game_id} points/score updated (cache and db) to: {points_left}/{points_right}")

@database_sync_to_async
def update_player_powerup(game_id, player_side, powerup, new_value):
    """
    The database only has a boolean for each powerup but on cache we have those
    values: available, using, used, unavailable

    The function will return if the powerup was updated successfully
    """
    # Deactivate the powerup if currently in use
    if new_value == 'used' and get_game_data(game_id, player_side, powerup) == 'using':
        set_game_data(game_id, player_side, powerup, new_value)
    elif new_value == 'using' and get_game_data(game_id, player_side, powerup) == 'available':
        set_game_data(game_id, player_side, powerup, 'using')
        set_game_data(game_id, 'gameData', 'sound', 'powerup')
    elif new_value == 'using':
        set_game_data(game_id, 'gameData', 'sound', 'no')
        return False
    else:
        return False

    # Update db
    # To be sure that the powerup is not updated twice only update for state 'using'
    if new_value == 'using':
        with transaction.atomic():
            user = get_user_of_game(game_id, player_side)
            game = Game.objects.get(id=game_id)
            game_member = GameMember.objects.select_for_update().get(game_id=game, user_id=user)
            if powerup == 'powerupBig':
                game_member.powerup_big = False
            elif powerup == 'powerupFast':
                game_member.powerup_fast = False
            elif powerup == 'powerupSlow':
                game_member.powerup_slow = False
            else:
                logging.error(f"Powerup {powerup} not found")
            game_member.save()
    return True
