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
    game_state_data = cache.get(f'game_{game_id}_state', {}) # TODO: REMOVE WHEN FINISHED #284
    if not game_state_data:
        logging.error(f"! can't update game state to{state} because game {game_id} is not in cache!")
    else:
        game_state_data['gameData']['state'] = state
        # TODO: REMOVE WHEN FINISHED #284
        cache.set(f'game_{game_id}_state', game_state_data, timeout=3000)

    # Update db
    with transaction.atomic():
        game = Game.objects.select_for_update().get(id=game_id)
        if (state == Game.GameState.FINISHED):
            # Use my finish_game function to deal with everything
            finish_game(game)
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
def update_player_powerup(game_id, player_side, powerup):
    # Update db
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
