from game.models import Game
from core.exceptions import BarelyAnException
from game.constants import GAME_STATE
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

async def init_game(game, consumer):
    logging.info(f"Game state: {game.state}") # pending
    # Check game state
    if game.state != Game.GameState.PENDING and game.state != Game.GameState.PAUSED:
        raise BarelyAnException(_("Game is not in a state to be started"))
    # Init game data on cache
    cache.set(f'game_{game.id}_state', deepcopy(GAME_STATE), timeout=3000)
    # Change database
    await update_game_state_db(game, Game.GameState.ONGOING)
