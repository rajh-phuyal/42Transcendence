from datetime import datetime, timedelta
from game.constants import GAME_STATE, GAME_PLAYER_INPUT
from copy import deepcopy
import asyncio
import random
from game.models import Game
from asgiref.sync import sync_to_async
import json
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
import logging
from chat.models import ConversationMember
from django.core.cache import cache
from django.utils.translation import gettext as _
from asgiref.sync import async_to_sync
from core.exceptions import BarelyAnException
from core.decorators import barely_handle_ws_exceptions
from services.chat_service import setup_all_conversations, send_total_unread_counter
from services.tournament_service import setup_all_tournament_channels
from services.websocket_utils import WebSocketMessageHandlersMain, WebSocketMessageHandlersGame, check_if_game_can_be_started, parse_message
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from game.constants import GAME_FPS, PADDLE_OFFSET
from game.utils_ws import update_game_state, update_game_points
from game.utils import is_left_player, get_game_data, set_game_data, get_player_input, get_user_of_game

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

    # @barely_handle_ws_exceptions TODO: Uncomment this line
    async def connect(self):
        # TODO: check if the user is in the game
        await super().connect()

        # Set self vars for consumer
        self.user_id = self.scope['user'].id
        logging.info(f"User id: {self.user_id}")
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        logging.info(f"Game id: {self.game_id}")
        self.game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        logging.info(f"Game: {self.game}")
        self.local_game = await database_sync_to_async(lambda: self.game.game_members.first().local_game)()
        logging.info(f"Local game: {self.local_game}")
        self.isLeftPlayer = await database_sync_to_async(is_left_player)(self.game_id, self.user_id)
        logging.info(f"Is left player: {self.isLeftPlayer}")
        self.leftPlayer =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerLeft')
        logging.info(f"Left player: {self.leftPlayer}")
        self.rightPlayer =  await database_sync_to_async(get_user_of_game)(self.game_id, 'playerRight')
        logging.info(f"Right player: {self.rightPlayer}")
        logging.info("Initialiazing consumer self vars: user_id %s, game_id: %s, local_game: %s, isLeftPlayer: %s", self.user_id, self.game_id, self.local_game, self.isLeftPlayer)

        # If the game is not in the right state, close the connection
        if self.game.state == Game.GameState.FINISHED or self.game.state == Game.GameState.QUITED:
            await self.close()
            logging.info(f"Game {self.game_id} is not in the right state to be played. CONNECTION CLOSED.")

        # Add client to the channel layer group
        game_name = f"game_{self.game_id}"
        await channel_layer.group_add(game_name, self.channel_name)

        # Accept the connection
        await self.accept()

        # Init game on cache
        await self.init_game_on_cache()
        await self.send_update_game_data_msg()

        # Set the player ready
        self.game.set_player_ready(self.scope['user'].id, True)
        await self.send_update_players_ready_msg()

        # If both users are ready start the loop
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftPlayer.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightPlayer.id)
        if left_ready and right_ready:
            # Start / Continue the loop
            # 1. Set start time and send it to channel
            start_time = datetime.now() + timedelta(seconds=5)
            start_time_formated = start_time.isoformat()
            logging.info(f"Game will start at: {start_time_formated}")
            await self.send_update_players_ready_msg(start_time_formated)

            # 2. Calculate the delay so the game loop start not before the start time
            delay = (start_time - datetime.now()).total_seconds()
            if delay > 0:
                await asyncio.sleep(delay)  # Wait until the start time

            # 3. Start the game loop
            GameConsumer.game_loops[self.game_id] = asyncio.create_task(GameConsumer.run_game_loop(self.game_id))

    #@barely_handle_ws_exceptions TODO: uncomment this line
    async def disconnect(self, close_code):
        await super().disconnect(close_code)

        # Remove client from the channel layer group
        await channel_layer.group_discard(f"game_{self.game_id}", self.channel_name)

        # Set the player NOT ready
        self.game.set_player_ready(self.scope['user'].id, False)
        await self.send_update_players_ready_msg()

        # If the game was ongoing, pause it
        game_state_data = cache.get(f'game_{self.game_id}_state', {})
        if game_state_data['gameData']['state'] == 'ongoing':
            # Set deadline to reconnection time
            # # TODO

            # Set game to paused
            await update_game_state(self.game_id, Game.GameState.PAUSED)

            # Other player scores that point
            user_id_for_point = self.leftPlayer.id
            if self.user_id == self.leftPlayer.id:
                user_id_for_point = self.rightPlayer.id
            await update_game_points(self.game_id, user_id_for_point)

            # Send the updated game state to FE
            self.send_update_game_data_msg()

    #@barely_handle_ws_exceptions  TODO: Uncomment this line
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
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftPlayer.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightPlayer.id)
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
        # CREATE GAME DATA ON CACHE IF DOESNT EXIST

        game_state_data = get_game_data (self.game_id)
        if not game_state_data:
            logging.info(f"Init game on cache: game_{self.game_id}_state")
            cache.set(f'game_{self.game_id}_state', deepcopy(GAME_STATE), timeout=3000)
            # Randomize serving player
            if random.randint(0, 1) == 0:
                set_game_data(self.game_id, 'gameData', 'playerServes', 'playerLeft')
                set_game_data(self.game_id, 'gameData', 'ballDirectionX', -1)
            else:
                set_game_data(self.game_id, 'gameData', 'playerServes', 'playerRight')
                set_game_data(self.game_id, 'gameData', 'ballDirectionX', 1)
            # Add a minimal random direction to the ball so it won't be stuck horizontally
            set_game_data(self.game_id, 'gameData', 'ballDirectionY', random.uniform(-0.01, 0.01))
            # TODO UNCOMMENT THIS LLINES BELOW
            set_game_data(self.game_id, 'gameData', 'ballDirectionY', 1)
            set_game_data(self.game_id, 'gameData', 'ballDirectionX', -0.5)

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
        # Updates the state to ongoing
        await update_game_state(game_id, Game.GameState.ONGOING)

        # Start the game loop
        logging.info(f"Game loop starts now: {game_id}")
        while get_game_data(game_id, 'gameData', 'state') == 'ongoing':
            try:
                # Fetches game state from cache
                game_state_data = cache.get(f'game_{game_id}_state', {})

                # Extract user state from game state
                game_state_data_left = game_state_data['playerLeft']
                game_state_data_right = game_state_data['playerRight']

                # Change postions of both paddles if requested and allowed
                move_paddle(game_id, 'playerLeft')
                move_paddle(game_id, 'playerRight')

                # Then calculate ball movement
                move_ball(game_id)
                apply_wall_bonce(game_id)
                check_paddle_bounce(game_id)

                # Send the updated game state to FE
                game_name = f"game_{game_id}"
                await channel_layer.group_send(
                    game_name,
                    {
                        "type": "update_game_state",
                        "messageType": "gameState",
                        **get_game_data(game_id)
                    }
                )

                check_if_game_is_finished(game_id)


                # Await for next frame render
                await asyncio.sleep(1 / GAME_FPS)
            except Exception as e:
                logging.error(f"Error in game loop: {e}")
                break
        logging.info(f"Game loop ended: {game_id}")
        if(get_game_data(game_id, 'gameData', 'state') == 'finished'):
            # Clear the game data on cache
            cache.delete(f'game_{game_id}_state')
            cache.delete(f'game_{game_id}_player_left')
            cache.delete(f'game_{game_id}_player_right')
            logging.info(f"Game was finished and cache cleared: {game_id}")
            # Inform both consumers to close the connection
            await channel_layer.group_send(
                game_name,
                {
                    "type": "game_finished",
                }
            )

# Player side needs to be 'playerLeft' or 'playerRight'
def move_paddle(game_id, playerSide):
    movePaddle = get_player_input(game_id, playerSide, 'movePaddle')
    if  movePaddle == '0':
        return

    new_paddle_pos = get_game_data(game_id, playerSide, 'paddlePos')
    paddle_speed = get_game_data(game_id, playerSide, 'paddleSpeed')
    paddle_size = get_game_data(game_id, playerSide, 'paddleSize')

    # Trying the player input
    if movePaddle == '+':
        new_paddle_pos += paddle_speed
    elif movePaddle == '-':
        new_paddle_pos -= paddle_speed

    # Validating / Adjusting the new paddle position
    if (new_paddle_pos - (paddle_size / 2)) < 0:
        new_paddle_pos = paddle_size / 2
    elif (new_paddle_pos + (paddle_size / 2)) > 100:
        new_paddle_pos = 100 - (paddle_size / 2)

    # Save the new paddle position
    set_game_data(game_id, playerSide, 'paddlePos', new_paddle_pos)

def move_ball(game_id):

    # Get from cache
    ball_pos_x = get_game_data(game_id, 'gameData', 'ballPosX')
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    ball_direction_x = get_game_data(game_id, 'gameData', 'ballDirectionX')
    ball_direction_y = get_game_data(game_id, 'gameData', 'ballDirectionY')
    ball_speed = get_game_data(game_id, 'gameData', 'ballSpeed')

    # Move the ball
    ball_pos_x += ball_direction_x * ball_speed
    ball_pos_y += ball_direction_y * ball_speed
    # TODO: change ball speed

    # Save the new ball position
    set_game_data(game_id, 'gameData', 'ballPosX', ball_pos_x)
    set_game_data(game_id, 'gameData', 'ballPosY', ball_pos_y)

def apply_wall_bonce(game_id):
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    ball_direction_y = get_game_data(game_id, 'gameData', 'ballDirectionY')
    # Apply wall bounce (Calculate if the upper or lower wall was hit)
    if ball_pos_y <= ball_radius:
        set_game_data(game_id, 'gameData', 'ballPosY', ball_radius)
        set_game_data(game_id, 'gameData', 'ballDirectionY', ball_direction_y * -1)
    elif ball_pos_y >= 100 - ball_radius:
        set_game_data(game_id, 'gameData', 'ballPosY', 100 - ball_radius)
        set_game_data(game_id, 'gameData', 'ballDirectionY', ball_direction_y * -1)
    else:
        # No wall bounce happend
        ...

def check_paddle_bounce(game_id):
    ball_pos_x = get_game_data(game_id, 'gameData', 'ballPosX')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')

    # Check if the ball is hitting the left or right paddle(point was scored)
    if ball_pos_x <= PADDLE_OFFSET + ball_radius:
        apply_padlle_hit(game_id, 'playerLeft')
    elif ball_pos_x >= 100 - PADDLE_OFFSET - ball_radius:
        apply_padlle_hit(game_id, 'playerRight')
    else:
        # No paddle bounce happend
        ...

# Only called when the x pos of ball is on the x of the paddle
def apply_padlle_hit(game_id, player_side):
    logging.info(f"Ball hit the paddle: {player_side}")
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    paddle_pos = get_game_data(game_id, player_side, 'paddlePos')
    paddle_size = get_game_data(game_id, player_side, 'paddleSize')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    logging.info(f"Ball pos y: {ball_pos_y}, paddle pos: {paddle_pos}, paddle size: {paddle_size}")

    # Check if a point was scored
    if ball_pos_y < paddle_pos:
        if ball_pos_y + ball_radius < paddle_pos - paddle_size / 2:
            apply_point(game_id, player_side)
        else:
            # Ball should bounce off up
            logging.info(f"Ball should bounce off up")
            distance_paddle_ball = paddle_pos - ball_pos_y
            percentage_y = distance_paddle_ball / (paddle_size / 2 + ball_radius)
            set_game_data(game_id, 'gameData', 'ballDirectionX', -1 * get_game_data(game_id, 'gameData', 'ballDirectionX'))
            set_game_data(game_id, 'gameData', 'ballDirectionY', -percentage_y)
    else:
        if ball_pos_y - ball_radius > paddle_pos + paddle_size / 2:
            apply_point(game_id, player_side)
        else:
            logging.info(f"Ball should bounce off down")
            distance_paddle_ball = ball_pos_y - paddle_pos
            percentage_y = distance_paddle_ball / (paddle_size / 2 + ball_radius)
            set_game_data(game_id, 'gameData', 'ballDirectionX', -1 * get_game_data(game_id, 'gameData', 'ballDirectionX'))
            set_game_data(game_id, 'gameData', 'ballDirectionY', percentage_y)

def apply_point(game_id, player_side):
    logging.info(f"Point scored by: {player_side}")
    # update_score_points in cache and db
    update_game_points(game_id, player_side=player_side)

    # Reset the ball
    set_game_data(game_id, 'gameData', 'ballPosX', 50)
    set_game_data(game_id, 'gameData', 'ballPosY', 50)
    set_game_data(game_id, 'gameData', 'ballSpeed', 1)
    set_game_data(game_id, 'gameData', 'ballDirectionY', random.uniform(-0.01, 0.01))

    # Check if extende mode should be activated (on the score of 10:10)
    if not get_game_data(game_id, 'gameData', 'extendingGameMode'):
        if get_game_data(game_id, 'playerLeft', 'points') == 10 and get_game_data(game_id, 'playerRight', 'points') == 10:
            set_game_data(game_id, 'gameData', 'extendingGameMode', True)

    # Set the next serve
    if get_game_data(game_id, 'gameData', 'extendingGameMode'):
        # 1 Serve each
        if get_game_data(game_id, 'gameData', 'playerServes') == 'playerLeft':
            set_game_data(game_id, 'gameData', 'playerServes', 'playerRight')
        else:
            set_game_data(game_id, 'gameData', 'playerServes', 'playerLeft')
    else:
        # 2 Serves each
        remaining_serves = get_game_data(game_id, 'gameData', 'remainingServes')
        if remaining_serves > 1:
            set_game_data(game_id, 'gameData', 'remainingServes', remaining_serves - 1)
        else:
            set_game_data(game_id, 'gameData', 'remainingServes', 2)
            if get_game_data(game_id, 'gameData', 'playerServes') == 'playerLeft':
                set_game_data(game_id, 'gameData', 'playerServes', 'playerRight')
            else:
                set_game_data(game_id, 'gameData', 'playerServes', 'playerLeft')
    if get_game_data(game_id, 'gameData', 'playerServes') == 'playerLeft':
        set_game_data(game_id, 'gameData', 'ballDirectionX', -1)
    else:
        set_game_data(game_id, 'gameData', 'ballDirectionX', 1)


def check_if_game_is_finished(game_id):
    score_left = get_game_data(game_id, 'playerLeft', 'points')
    score_right = get_game_data(game_id, 'playerRight', 'points')
    if get_game_data(game_id, 'gameData', 'extendingGameMode'):
        # One player needs to points ahead
        if abs(score_left - score_right) >= 2:
            update_game_state(game_id, Game.GameState.FINISHED)
    else:
        # One player needs to score 11 points
        if score_left >= 11 or score_right >= 11:
            update_game_state(game_id, Game.GameState.FINISHED)