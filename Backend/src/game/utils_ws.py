from game.models import Game
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
    cache.set(f'game_{game.id}_state', deepcopy(GAME_STATE), timeout=3000)
    cache.set(f'game_{game.id}_player_left', deepcopy(GAME_PLAYER_INPUT), timeout=3000)
    cache.set(f'game_{game.id}_player_right', deepcopy(GAME_PLAYER_INPUT), timeout=3000)

    # Change database
    await update_game_state_db(game, Game.GameState.ONGOING)
