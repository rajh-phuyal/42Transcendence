# Basics
import logging, random
from datetime import datetime
from copy import deepcopy
# DJANGO STUFF
from django.core.cache import cache
from django.utils.translation import gettext as _
# GAME STUFF
from game.constants import GAME_PLAYER_INPUT, GAME_STATE, PADDLE_OFFSET
from services.constants import PRE_DATA_GAME

async def init_game_on_cache(game, leftMember, rightMember):
    """ Just for making sure all the game data is initialized on cache """

    async def init_powerup(game, value, key1, key2):
        """
        Need to compare if the game has powerups or not
        to if the users still has powerups left to set state to:
        available / using / used / unavailable
        """
        if game.powerups:
            if value:
                set_game_data(game.id, key1, key2, 'available')
            else:
                set_game_data(game.id, key1, key2, 'used')
        else:
            set_game_data(game.id, key1, key2, 'unavailable')

    game_state_data = get_game_data (game.id)
    if not game_state_data:
        cache_key = f'{PRE_DATA_GAME}{game.id}'
        logging.info(f"Init game on cache: game_data: {cache_key}")
        cache.set(cache_key, deepcopy(GAME_STATE), timeout=3000)
        # Initialize the game data to match the db:
        set_game_data(game.id, 'gameData', 'state', game.state)
        set_game_data(game.id, 'gameData', 'deadline', game.deadline)
        set_game_data(game.id, 'playerLeft', 'points', leftMember.points)
        set_game_data(game.id, 'playerRight', 'points', rightMember.points)
        set_game_data(game.id, 'playerLeft', 'result', leftMember.result)
        set_game_data(game.id, 'playerRight', 'result', rightMember.result)
        await init_powerup(game, leftMember.powerup_big, 'playerLeft', 'powerupBig')
        await init_powerup(game, leftMember.powerup_slow, 'playerLeft', 'powerupSlow')
        await init_powerup(game, leftMember.powerup_fast, 'playerLeft', 'powerupFast')
        await init_powerup(game, rightMember.powerup_big, 'playerRight', 'powerupBig')
        await init_powerup(game, rightMember.powerup_slow, 'playerRight', 'powerupSlow')
        await init_powerup(game, rightMember.powerup_fast, 'playerRight', 'powerupFast')

        # Randomize serving player
        if random.randint(0, 1) == 0:
            set_game_data(game.id, 'gameData', 'playerServes', 'playerLeft')
            set_game_data(game.id, 'ball', 'directionX', -1)
            set_game_data(game.id, 'ball', 'posX', 100 - PADDLE_OFFSET)
        else:
            set_game_data(game.id, 'gameData', 'playerServes', 'playerRight')
            set_game_data(game.id, 'ball', 'directionX', 1)
            set_game_data(game.id, 'ball', 'posX', PADDLE_OFFSET)
        # Add a minimal random direction to the ball so it won't be stuck horizontally
        set_game_data(game.id, 'ball', 'directionY', random.uniform(-0.01, 0.01))

    # CREATE LEFT PLAYER INPUT ON CACHE IF DOESNT EXIST
    input_player_left = get_player_input(game.id, 'playerLeft')
    if not input_player_left:
        cache_key = f'{PRE_DATA_GAME}{game.id}_input_playerLeft'
        logging.info(f"Init game on cache: playerLeft Input: {cache_key}")
        cache.set(cache_key, deepcopy(GAME_PLAYER_INPUT), timeout=3000)

    # CREATE RIGHT PLAYER INPUT ON CACHE IF DOESNT EXIST
    input_player_right = get_player_input(game.id, 'playerRight')
    if not input_player_right:
        cache_key = f'{PRE_DATA_GAME}{game.id}_input_playerRight'
        logging.info(f"Init game on cache: playerRight Input: {cache_key}")
        cache.set(cache_key, deepcopy(GAME_PLAYER_INPUT), timeout=3000)

def set_player_input(game_id, side, playerInfo):
    """
    Helper function to set the player data on cache.
    Should only be triggered by incoming websocket messages.
    """
    cache_key = f'{PRE_DATA_GAME}{game_id}_input_{side}'
    cache.set(cache_key, playerInfo, timeout=3000)

def get_player_input(game_id, side, key1=None):
    """
    Helper function to get the player data from cache e.g:
    get_player_input(1, 'playerLeft', 'up') -> returns the value of playerLeft['up']
    """
    cache_key = f'{PRE_DATA_GAME}{game_id}_input_{side}'
    if (input_player := cache.get(cache_key)):
        if not key1:
            return input_player
        if key1 not in input_player:
            logging.error(f"! Key '{key1}' does not exist in " + cache_key + " cache!")
            return None
        return input_player[key1]
    else:
        logging.error("! Can't get game player input because " +  cache_key + " is not in cache!")

def set_game_data(game_id, key1, key2, new_value, timeout=3000):
    """
    Helper function to set the game data on cache e.g:
    set_game_data(1, 'gameData', 'state', 'playing') -> sets gameData['state'] to 'playing'
    """
    cache_key = f'{PRE_DATA_GAME}{game_id}'
    if (game_state_data := cache.get(cache_key)):
        if key1 in game_state_data and key2 in game_state_data[key1]:
            # If it's a datetime, convert it to iso format string
            if isinstance(new_value, datetime):
                new_value = new_value.isoformat()
            game_state_data[key1][key2] = new_value
            cache.set(cache_key, game_state_data, timeout=timeout)
            return True
        logging.error(f"! Key '{key1}' or '{key2}' does not exist in game {game_id} cache!")
    else:
        ...
        # logging.error(f"! Can't update game state because game {game_id} is not in cache! This isn't to bad :D")
    return False

def get_game_data(game_id, key1=None, key2=None):
    """
    Helper function to get the game data from cache e.g:
    get_game_data(1, 'gameData', 'state') -> returns the value of gameData['state']
    """
    cache_key = f'{PRE_DATA_GAME}{game_id}'
    if (game_state_data := cache.get(cache_key)):
        if not key1:
            return game_state_data
        elif key1 not in game_state_data:
            logging.error(f"! Key '{key1}' does not exist in game {game_id} cache!")
            return None
        if game_state_data_key1 := game_state_data[key1]:
            if not key2:
                return game_state_data_key1
            elif key2 not in game_state_data_key1:
                logging.error(f"! Key '{key2}' does not exist in game {game_id} cache!")
                return None
            return game_state_data_key1[key2]
    else:
        ...
        # logging.error(f"! Can't get game state because game {game_id} is not in cache! Not to bad I hope :D")

async def delete_game_from_cache(game_id):
    """ Deletes the game data from cache """
    cache_key = f'{PRE_DATA_GAME}{game_id}'
    cache.delete(cache_key)
    cache_key = f'{PRE_DATA_GAME}{game_id}_input_playerLeft'
    cache.delete(cache_key)
    cache_key = f'{PRE_DATA_GAME}{game_id}_input_playerRight'
    cache.delete(cache_key)
