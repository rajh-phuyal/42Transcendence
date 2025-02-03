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

@database_sync_to_async
def update_game_state_db(game, state):
    # TODO:
    # just update cache
    # and update db without await
    # if tournament game
    #      inform tournament guys (gameUpdateState)
    # if game is finished
    #     remove_game_from_cache



    logging.info(f"Game state before: {game.state}")
    game.state = state
    game.save()
    logging.info(f"Game state after: {game.state}")





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
    await update_game_state_db(game, Game.GameState.ONGOING)

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


