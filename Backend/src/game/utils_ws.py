from game.utils import is_left_player, get_game_data, set_game_data, get_player_input, get_user_of_game
import random
from game.models import Game, GameMember
from core.exceptions import BarelyAnException
from game.constants import GAME_STATE, GAME_PLAYER_INPUT
from django.core.cache import cache
from copy import deepcopy
from django.utils.translation import gettext as _
import logging
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.db import transaction
from game.utils import is_left_player, finish_game, get_user_of_game

@database_sync_to_async
def update_game_state(game_id, state):
    # Update cache
    game_state_data = cache.get(f'game_{game_id}_state', {})
    if not game_state_data:
        logging.error(f"! can't update game state to{state} because game {game_id} is not in cache!")
    else:
        game_state_data['gameData']['state'] = state
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

# TODO: below is old code!!!!



# This will:
# - Check if the game is in a state to be started
# - Initialize the game state in cache
# - Randomize the serving player
# - Set the game state to ONGOING in db
async def init_game(game):
    logging.info(f"Game state 1: {game.state}")

    # Check game state
    if game.state not in [Game.GameState.PENDING, Game.GameState.PAUSED]:
        raise BarelyAnException(_("Game is not in a state to be started"))

    # Change database
    await update_game_state(game, Game.GameState.ONGOING)

    logging.info(f"Game state 2: {game.state}")
    # Init game data on cache (if is the first time)
    old_cache_data = cache.get(f'game_{game.id}_state')
    if old_cache_data:
        logging.info(f"Game state 2.5: {old_cache_data}")
        old_cache_data['gameData']['state'] = 'ongoing'
        cache.set(f'game_{game.id}_state', old_cache_data, timeout=3000)
        return

    new_game_state = deepcopy(GAME_STATE)
    # Randomize serving player
    if random.randint(0, 1) == 0:
        new_game_state["gameData"]["playerServes"] = "playerLeft"
        new_game_state["gameData"]["ballDirectionX"] = -1
    else:
        new_game_state["gameData"]["playerServes"] = "playerRight"
        new_game_state["gameData"]["ballDirectionX"] = 1
    logging.info(f"Game state 3: {game.state}")
    new_game_state['gameData']['ballDirectionY'] = random.uniform(-0.01, 0.01)

    # Check if the game is a local game
    logging.info(f"Game state 4: {game.state}")
    game_member = await database_sync_to_async(lambda: GameMember.objects.filter(game=game).first())()
    logging.info(f"Game state 5: {game_member}")
    logging.info(f"Game state 6: {game_member.local_game}")

    new_game_state['gameData']['localGame'] = game_member.local_game
    logging.info(f"Cache game {game.id} localGame: {new_game_state['gameData']['localGame']}")


    cache.set(f'game_{game.id}_state', new_game_state, timeout=3000)
    cache.set(f'game_{game.id}_player_left', deepcopy(GAME_PLAYER_INPUT), timeout=3000)
    cache.set(f'game_{game.id}_player_right', deepcopy(GAME_PLAYER_INPUT), timeout=3000)
    logging.info(f"Game state 6: {game.state}")


