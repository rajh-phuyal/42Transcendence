import random
from game.models import Game, GameMember
from core.exceptions import BarelyAnException
from game.constants import GAME_STATE, GAME_PLAYER_INPUT
from django.core.cache import cache
from copy import deepcopy
from django.utils.translation import gettext as _
import logging
from channels.db import database_sync_to_async

@database_sync_to_async
def update_game_state_db(game, state):
    logging.info(f"Game state before: {game.state}")
    game.state = state
    game.save()
    logging.info(f"Game state after: {game.state}")

async def init_game(game):
    logging.info(f"Game state: {game.state}")

    # Check game state
    if game.state not in [Game.GameState.PENDING, Game.GameState.PAUSED]:
        raise BarelyAnException(_("Game is not in a state to be started"))

    # Init game data on cache
    new_game_state = deepcopy(GAME_STATE)
    # Randomize serving player
    if random.randint(0, 1) == 0:
        new_game_state["gameData"]["playerServes"] = "playerLeft"
        new_game_state["gameData"]["ballDirectionX"] = -1
    else:
        new_game_state["gameData"]["playerServes"] = "playerRight"
        new_game_state["gameData"]["ballDirectionX"] = 1
    new_game_state['gameData']['ballDirectionY'] = random.uniform(-0.01, 0.01)

    # Check if the game is a local game
    gameMember = GameMember.objects.filter(game=game).first()
    new_game_state['gameData']['localGame'] = gameMember.local_game
    cache.set(f'game_{game.id}_state', new_game_state, timeout=3000)
    cache.set(f'game_{game.id}_player_left', deepcopy(GAME_PLAYER_INPUT), timeout=3000)
    cache.set(f'game_{game.id}_player_right', deepcopy(GAME_PLAYER_INPUT), timeout=3000)

    # Change database
    await update_game_state_db(game, Game.GameState.ONGOING)
