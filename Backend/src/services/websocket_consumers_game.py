# Basics
import logging, asyncio, json, math
from datetime import datetime, timedelta, timezone
# Django
from django.utils.translation import gettext as _
# Core
from core.decorators import barely_handle_ws_exceptions
# Game stuff
from game.constants import GAME_FPS, GAME_COUNTDOWN_MAX
from game.models import Game
from game.utils import is_left_player, get_user_of_game
from game.utils_ws import update_game_state
from game.game_cache import get_game_data, set_game_data, init_game_on_cache, delete_game_from_cache
from game.game_physics import activate_power_ups, move_paddle, move_ball, apply_wall_bonce, check_paddle_bounce, check_if_game_is_finished, apply_point
# Services
from services.constants import PRE_GROUP_GAME
from services.websocket_consumers_base import CustomWebSocketLogic
from services.websocket_handler_game import WebSocketMessageHandlersGame
from services.send_ws_msg import send_ws_game_data_msg, send_ws_game_players_ready_msg, send_ws_game_finished
# Channels
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()

# Manages the temporary WebSocket connection for a single game
class GameConsumer(CustomWebSocketLogic):
    game_loops = {}

    @barely_handle_ws_exceptions
    async def connect(self):
        await super().connect()
        # Set self vars for consumer
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game = await database_sync_to_async(Game.objects.get)(id=self.game_id)

        # CHECK IF CLIENT IS ALLOWED TO CONNECT
        # Check if the client is a game member...
        if not await database_sync_to_async(lambda: self.game.game_members.filter(user=self.user).exists())():
            logging.info(f"User {self.user.id} is not a member of game: entering viewer mode.")
            group_name = f"{PRE_GROUP_GAME}{self.game_id}"
            await channel_layer.group_add(group_name, self.channel_name)
            await self.accept()
            await send_ws_game_data_msg(self.game_id)
            return

        # Check if game is part of a local tournament...
        if self.game.tournament and self.game.tournament.local_tournament:
            # ... only the admin can connect to the game
            admin = await database_sync_to_async(lambda: self.game.tournament.members.filter(is_admin=True).first())()
            if self.user.id != admin.user.id:
                logging.info(f"User {self.user.id} is not the admin of the local tournament game {self.game_id}. CONNECTION CLOSED.")
                await self.close()
        # If the game is not in the right state, close the connection
        if self.game.state == Game.GameState.FINISHED or self.game.state == Game.GameState.QUITED:
            await self.close()
            logging.info(f"Game {self.game_id} is not in the right state to be played. CONNECTION CLOSED.")
        # Add client to the channel layer group
        # Note: here i can't use update_client_in_group since this always uses the main ws connection!
        group_name = f"{PRE_GROUP_GAME}{self.game_id}"
        await channel_layer.group_add(group_name, self.channel_name)
        # Accept the connection
        await self.accept()

        # CLIENT IS NOW CONNECTED
        self.isLeftPlayer = await database_sync_to_async(is_left_player)(self.game_id, self.user.id)
        self.leftUser =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerLeft')
        self.rightUser =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerRight')
        self.leftMember = await database_sync_to_async(self.game.game_members.get)(user=self.leftUser)
        self.rightMember = await database_sync_to_async(self.game.game_members.get)(user=self.rightUser)
        # Init game on cache and send the game data
        await init_game_on_cache(self.game, self.leftMember, self.rightMember)
        await send_ws_game_data_msg(self.game_id)

        # SETTING PLAYER(S) READY
        if self.game.tournament and self.game.tournament.local_tournament:
            # CASE: A local tournament game: so we need to set both players ready
            await database_sync_to_async(self.game.set_player_ready)(self.leftUser.id, True)
            await database_sync_to_async(self.game.set_player_ready)(self.rightUser.id, True)
        else:
            # NORMAL CASE: Set only the client ready
            await database_sync_to_async(self.game.set_player_ready)(self.user.id, True)
        # Send the player ready message and the game data
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        await send_ws_game_players_ready_msg(self.game_id, left_ready, right_ready)
        await send_ws_game_data_msg(self.game_id)
        # If both users are ready start the loop
        if left_ready and right_ready:
            asyncio.create_task(self.start_the_game()) # To not block the connect function

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Remove client from the channel layer group
        # Note: here i can't use update_client_in_group since this always uses the main ws connection!
        group_name = f"{PRE_GROUP_GAME}{self.game_id}"
        await channel_layer.group_discard(group_name, self.channel_name)
        # Set the player NOT ready
        self.game.set_player_ready(self.user.id, False)
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        await send_ws_game_players_ready_msg(self.game_id, left_ready, right_ready)
        # If the game was ongoing, pause it
        if get_game_data(self.game_id, 'gameData', 'state') == 'ongoing':
            # # TODO: issue#307
            # Set deadline to reconnection time

            # Set game to paused
            await update_game_state(self.game_id, Game.GameState.PAUSED)
            set_game_data(self.game_id, 'gameData', 'sound', 'pause')

            # Other player scores that point
            player_side = 'playerRight'
            if self.user.id == self.leftUser.id:
                player_side = 'playerLeft'
            await apply_point(self.game_id, player_side)

            # Send the updated game state to FE
            await send_ws_game_data_msg(self.game_id)
            set_game_data(self.game_id, 'gameData', 'sound', 'none')

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Process the message
        await WebSocketMessageHandlersGame()[f"{self.message_type}"](self, text_data)

    async def update_players_ready(self, event):
        await self.send(text_data=json.dumps({**event}))
    async def update_game_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def game_finished(self, event):
        # This is triggerd by the end of the game loop to close the connection
        await self.close()

    async def start_the_game(self):
        # Start / Continue the loop
        # 1. Set start time and send it to channel
        start_time = datetime.now(timezone.utc) + timedelta(seconds=GAME_COUNTDOWN_MAX)
        start_time_formated = start_time.isoformat()
        logging.info(f"Game will start at: {start_time_formated}")
        await send_ws_game_players_ready_msg(self.game_id, True, True, start_time_formated)
        # Updates the state to countdown
        await update_game_state(self.game_id, Game.GameState.COUNTDOWN)
        await send_ws_game_data_msg(self.game_id)
        # 2. Calculate the delay so the game loop start not before the start time
        delay = (start_time - datetime.now(timezone.utc)).total_seconds()
        if delay > 0:
            await asyncio.sleep(math.floor(delay))  # Wait until the start time
        # 3. Start the game loop
        if get_game_data(self.game_id, 'gameData', 'state') != Game.GameState.COUNTDOWN:
            logging.info(f"Game loop was not started because the game state is not countdown: {self.game_id}. This isn't a problem. Mostlikely the game was paused again before the countdown finihed...")
            return

        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        if not left_ready or not right_ready:
            logging.info(f"Game loop was not started because one of the players is not ready: {self.game_id}. This isn't a problem. Mostlikely the game was paused again before the countdown finihed...")
            return

        GameConsumer.game_loops[self.game_id] = asyncio.create_task(GameConsumer.run_game_loop(self.game_id))

    @staticmethod
    async def run_game_loop(game_id):
        # Start the game loop
        logging.info(f"Game loop starts now: {game_id}")
        # Set state to ongoing
        await update_game_state(game_id, Game.GameState.ONGOING)
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
                await send_ws_game_data_msg(game_id)
                # Check if the game is finished (this will set the state to finished -> so the loop will end)
                await check_if_game_is_finished(game_id)
                # Await for next frame render
                await asyncio.sleep(1 / GAME_FPS)
            except Exception as e:
                logging.error(f"Error in game loop: {e}")
                break
        logging.info(f"Game loop ended: {game_id}")
        # To make sure the client has got the most up to date game state send it again
        await send_ws_game_data_msg(game_id)
        if (get_game_data(game_id, 'gameData', 'state') == 'finished') or (get_game_data(game_id, 'gameData', 'state') == 'quited'):
            delete_game_from_cache(game_id)
            logging.info(f"Game was finished and cache cleared: {game_id}")
            # Inform both consumers to close their connection
            await send_ws_game_finished(game_id)
