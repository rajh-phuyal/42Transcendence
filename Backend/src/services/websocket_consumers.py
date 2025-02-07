# Basics
import logging, asyncio, random, json
# Python stuff
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from copy import deepcopy
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_ws_exceptions
# Game stuff
from game.constants import GAME_FPS, GAME_STATE, GAME_PLAYER_INPUT, PADDLE_OFFSET
from game.models import Game
from game.utils import is_left_player, get_game_data, set_game_data, get_user_of_game
from game.utils_ws import update_game_state, update_game_points
from game.game_physics import activate_power_ups, move_paddle, move_ball, apply_wall_bonce, check_paddle_bounce, check_if_game_is_finished
# Services
from services.websocket_utils import WebSocketMessageHandlersMain, WebSocketMessageHandlersGame, parse_message
from services.chat_service import setup_all_conversations, send_total_unread_counter
from services.tournament_service import setup_all_tournament_channels
# Channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
channel_layer = get_channel_layer()

# Basic Connect an Disconnet functions for the WebSockets
class CustomWebSocketLogic(AsyncWebsocketConsumer):

    # Don't add a decorator here, it will be added in the child classes
    async def connect(self):
        logging.info("Opening WebSocket connection...")
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        else:
            logging.info("...for user: %s", self.scope['user'])
            return True

    # Don't add a decorator here, it will be added in the child classes
    async def disconnect(self, close_code):
        logging.info("Closing WebSocket connection...")
        # Ensure user is authenticated
        if self.scope['user'] == AnonymousUser():
            logging.error("User is not authenticated.")
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        else:
            logging.info("...for user: %s", self.scope['user'])

    # Don't add a decorator here, it will be added in the child classes
    async def receive(self, text_data):
        # Check again if authenticated
        if not self.scope['user'].is_authenticated:
            await self.close()
            raise BarelyAnException(_("User is not authenticated."))
        # Parse the message (only the messageType is required at this point)
        self.message_type = parse_message(text_data, mandatory_keys=[
                                          'messageType']).get('messageType')
        # logging.info(f"Received Websocket Message type: {self.message_type}")

    def update_user_last_seen(self, user):
        user.last_seen = timezone.now()  # TODO: Issue #193
        user.save(update_fields=['last_seen'])

# Manages the WebSocket connection for all pages after login
class MainConsumer(CustomWebSocketLogic):
    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        user = self.scope['user']
        # Setting the user's online status in cache
        user.set_online_status(True)
        # Store the WebSocket channel to the cache with the user ID as the key
        cache.set(f'user_channel_{user.id}', self.channel_name, timeout=3000)
        # Add the user to all their conversation groups
        await setup_all_conversations(user, self.channel_name, intialize=True)
        # Add the user to all their toruanemnt groups
        await setup_all_tournament_channels(user, self.channel_name, intialize=True)
        # Accept the connection
        await self.accept()
        # Send the inizial badge nummer
        await send_total_unread_counter(user.id)

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        user = self.scope['user']
        # Set the last login time for the user
        await sync_to_async(user.update_last_seen)()
        # Remove the user's online status from cache
        user.set_online_status(False)
        # Remove the user's WebSocket channel from cache
        cache.delete(f'user_channel_{user.id}')
        logging.info(f"User {user.username} marked as offline.")
        # Remove the user from all their conversation groups
        await setup_all_conversations(user, self.channel_name, intialize=False)
        # Remove the user from all their toruanemnt groups
        await setup_all_tournament_channels(user, self.channel_name, intialize=False)

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Setting the user
        user = self.scope['user']
        # Process the message
        await WebSocketMessageHandlersMain()[f"{self.message_type}"](self, user, text_data)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def update_badge(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def new_conversation(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_subscription(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def tournament_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def info(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_create(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_set_deadline(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_score(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_update_rank(self, event):
        await self.send(text_data=json.dumps({**event}))

# Manages the temporary WebSocket connection for a single game
class GameConsumer(CustomWebSocketLogic):
    game_loops = {}

    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()

        # Set self vars for consumer
        self.user_id = self.scope['user'].id
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        self.local_game = await database_sync_to_async(lambda: self.game.game_members.first().local_game)()
        self.isLeftPlayer = await database_sync_to_async(is_left_player)(self.game_id, self.user_id)
        self.leftUser =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerLeft')
        self.rightUser =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerRight')
        self.leftMember = await database_sync_to_async(self.game.game_members.get)(user=self.leftUser)
        self.rightMember = await database_sync_to_async(self.game.game_members.get)(user=self.rightUser)
        self.group_name = f"game_{self.game_id}"
        logging.info("Initialiazing consumer self vars: user_id %s, game_id: %s, local_game: %s, isLeftPlayer: %s", self.user_id, self.game_id, self.local_game, self.isLeftPlayer)

        # TODO: check if the user is a game member if not close the connection
        # Also keeP in mind local games!  issue #312

        # If the game is not in the right state, close the connection
        if self.game.state == Game.GameState.FINISHED or self.game.state == Game.GameState.QUITED:
            await self.close()
            logging.info(f"Game {self.game_id} is not in the right state to be played. CONNECTION CLOSED.")

        # Add client to the channel layer group
        await channel_layer.group_add(self.group_name, self.channel_name)

        # Accept the connection
        await self.accept()

        # Init game on cache
        await self.init_game_on_cache()

        # Set the player(s) ready
        if self.local_game:
            # On local games just set both players to ready #TODO: this works and is related to issue #312
            self.game.set_player_ready(self.leftUser.id, True)
            self.game.set_player_ready(self.rightUser.id, True)
        else:
            self.game.set_player_ready(self.user_id, True)
        # Send the player ready message and the game data
        await self.send_update_players_ready_msg()
        await self.send_update_game_data_msg()

        # If both users are ready start the loop
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        if left_ready and right_ready:
            # Start / Continue the loop
            # 1. Set start time and send it to channel
            start_time = datetime.now() + timedelta(seconds=5)
            start_time_formated = start_time.isoformat()
            logging.info(f"Game will start at: {start_time_formated}")
            await self.send_update_players_ready_msg(start_time_formated)

            # Updates the state to ongoing
            #TODO: this should be done only if the game loop actually starts but than
            # the frontend loops stops so maybe its fine here since it works
            await update_game_state(self.game_id, Game.GameState.ONGOING)

            # 2. Calculate the delay so the game loop start not before the start time
            delay = (start_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)  # Wait until the start time

            # 3. Start the game loop
            GameConsumer.game_loops[self.game_id] = asyncio.create_task(GameConsumer.run_game_loop(self.game_id))

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)

        # Remove client from the channel layer group
        await channel_layer.group_discard(self.group_name, self.channel_name)

        # Set the player NOT ready
        self.game.set_player_ready(self.user_id, False)
        await self.send_update_players_ready_msg()

        # If the game was ongoing, pause it
        game_state_data = cache.get(f'game_{self.game_id}_state', {})
        if game_state_data['gameData']['state'] == 'ongoing':
            # # TODO: issue#307
            # Set deadline to reconnection time

            # Set game to paused
            await update_game_state(self.game_id, Game.GameState.PAUSED)
            set_game_data(self.game_id, 'gameData', 'sound', 'pause')

            # Other player scores that point
            user_id_for_point = self.leftUser.id
            if self.user_id == self.leftUser.id:
                user_id_for_point = self.rightUser.id
            await update_game_points(self.game_id, user_id_for_point)

            # Send the updated game state to FE
            await self.send_update_game_data_msg()
            set_game_data(self.game_id, 'gameData', 'sound', 'none')

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Setting the user
        user = self.scope['user']
        # Process the message
        await WebSocketMessageHandlersGame()[f"{self.message_type}"](self, user, text_data)

    @barely_handle_ws_exceptions # TODO: Not sure if all the functions need this since the function calling this already has it
    async def update_players_ready(self, event):
        await self.send(text_data=json.dumps({**event}))

    @barely_handle_ws_exceptions # TODO: Not sure if all the functions need this since the function calling this already has it
    async def update_game_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    @barely_handle_ws_exceptions # TODO: Not sure if all the functions need this since the function calling this already has it
    async def game_finished(self, event):
        # This is triggerd by the end of the game loop to close the connection
        await self.close()

    @barely_handle_ws_exceptions # TODO: Not sure if all the functions need this since the function calling this already has it
    async def send_update_players_ready_msg(self, start_time = None):
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        await channel_layer.group_send(
            f"game_{self.game_id}",
            {
                "type": "update_players_ready",
                "messageType": "playersReady",
                "playerLeft": left_ready,
                "playerRight": right_ready,
                "startTime": start_time
            }
        )

    @barely_handle_ws_exceptions # TODO: Not sure if all the functions need this since the function calling this already has it
    async def send_update_game_data_msg(self):
        game_state_data = cache.get(f'game_{self.game_id}_state', {})
        if not game_state_data:
            logging.error(f"Game state not found for game {self.game_id} so it can't be send as a ws message!")
            return
        game_name = f"game_{self.game_id}"
        await channel_layer.group_send(
            game_name,
            {
                "type": "update_game_state",
                "messageType": "gameState",
                **game_state_data
            }
        )
        logging.info(f"Game state sent to group {game_name}")


    # Just for making sure all the game data is initialized on cache
    async def init_game_on_cache(self):
        # TODO: this here should already be working but is realted to issue #308
        # Need to compare if the game has powerups or not
        # to if the users still has powerups left to set state to:
        # available / using / used / unavailable
        async def init_powerup(self, value, key1, key2):
            if self.game.powerups:
                if value:
                    set_game_data(self.game_id, key1, key2, 'available')
                else:
                    set_game_data(self.game_id, key1, key2, 'used')
            else:
                set_game_data(self.game_id, key1, key2, 'unavailable')

        game_state_data = get_game_data (self.game_id)
        if not game_state_data:
            logging.info(f"Init game on cache: game_{self.game_id}_state")
            cache.set(f'game_{self.game_id}_state', deepcopy(GAME_STATE), timeout=3000)
            # Initialize the game data to match the db:
            set_game_data(self.game_id, 'gameData', 'state', self.game.state)
            set_game_data(self.game_id, 'playerLeft', 'points', self.leftMember.points)
            set_game_data(self.game_id, 'playerRight', 'points', self.rightMember.points)
            await init_powerup(self, self.leftMember.powerup_big, 'playerLeft', 'powerupBig')
            await init_powerup(self, self.leftMember.powerup_slow, 'playerLeft', 'powerupSlow')
            await init_powerup(self, self.leftMember.powerup_fast, 'playerLeft', 'powerupFast')
            await init_powerup(self, self.rightMember.powerup_big, 'playerRight', 'powerupBig')
            await init_powerup(self, self.rightMember.powerup_slow, 'playerRight', 'powerupSlow')
            await init_powerup(self, self.rightMember.powerup_fast, 'playerRight', 'powerupFast')

            # Randomize serving player
            if random.randint(0, 1) == 0:
                set_game_data(self.game_id, 'gameData', 'playerServes', 'playerLeft')
                set_game_data(self.game_id, 'ball', 'directionX', -1)
                set_game_data(self.game_id, 'ball', 'posX', 100 - PADDLE_OFFSET)
            else:
                set_game_data(self.game_id, 'gameData', 'playerServes', 'playerRight')
                set_game_data(self.game_id, 'ball', 'directionX', 1)
                set_game_data(self.game_id, 'ball', 'posX', PADDLE_OFFSET)
            # Add a minimal random direction to the ball so it won't be stuck horizontally
            set_game_data(self.game_id, 'ball', 'directionY', random.uniform(-0.01, 0.01))

        # CREATE LEFT PLAYER INPUT ON CACHE IF DOESNT EXIST
        cache_key = f'game_{self.game_id}_playerLeft'
        input_player_left = cache.get(cache_key, {})
        if not input_player_left:
            logging.info(f"Init game on cache: {cache_key}")
            cache.set(cache_key, deepcopy(GAME_PLAYER_INPUT), timeout=3000)

        # CREATE RIGHT PLAYER INPUT ON CACHE IF DOESNT EXIST
        cache_key = f'game_{self.game_id}_playerRight'
        input_player_right = cache.get(cache_key, {})
        if not input_player_right:
            logging.info(f"Init game on cache: {cache_key}")
            cache.set(cache_key, deepcopy(GAME_PLAYER_INPUT), timeout=3000)

    @staticmethod
    async def run_game_loop(game_id):
        # Start the game loop
        logging.info(f"Game loop starts now: {game_id}")
        while get_game_data(game_id, 'gameData', 'state') == 'ongoing':
            try:
                # Reset sound
                set_game_data(game_id, 'gameData', 'sound', 'none')
                # Activate PowerUps (if requested and allowed)
                await activate_power_ups(game_id, 'playerLeft')
                await activate_power_ups(game_id, 'playerRight')
                # Change postions of both paddles (if requested and allowed)
                await move_paddle(game_id, 'playerLeft')
                await move_paddle(game_id, 'playerRight')
                # Calculate ball movement
                await move_ball(game_id)
                await apply_wall_bonce(game_id)
                await check_paddle_bounce(game_id)
                # Send the updated game state to FE
                game_name = f"game_{game_id}"           # TODO: this should go in  a function!
                await channel_layer.group_send(         #
                    game_name,                          #
                    {                                   #
                        "type": "update_game_state",    #
                        "messageType": "gameState",     #
                        **get_game_data(game_id)        #
                    }                                   #
                )                                       #

                # Check if the game is finished (this will set the state to finished -> so the loop will end)
                await check_if_game_is_finished(game_id)
                # Await for next frame render
                await asyncio.sleep(1 / GAME_FPS)
            except Exception as e:
                logging.error(f"Error in game loop: {e}")
                break
        logging.info(f"Game loop ended: {game_id}")
        # To make sure the client has got the most up to date game state send it again
        # Send the updated game state to FE

        game_name = f"game_{game_id}"       # TODO: this should go in  a function!
        await channel_layer.group_send(
            game_name,
            {
                "type": "update_game_state",
                "messageType": "gameState",
                **get_game_data(game_id)
            }
        )

        if(get_game_data(game_id, 'gameData', 'state') == 'finished'):
            # Clear the game data on cache
            cache.delete(f'game_{game_id}_state')
            cache.delete(f'game_{game_id}_player_left')
            cache.delete(f'game_{game_id}_player_right')
            logging.info(f"Game was finished and cache cleared: {game_id}")
            # Inform both consumers to close their connection
            await channel_layer.group_send(game_name, {"type": "game_finished"})
