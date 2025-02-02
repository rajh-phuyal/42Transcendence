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
from services.websocket_utils import WebSocketMessageHandlersMain, WebSocketMessageHandlersGame, send_player_ready_state, parse_message
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from game.constants import GAME_FPS, PADDLE_OFFSET
from game.utils_ws import init_game
from game.utils_ws import update_game_state_db


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
        # TODO: check if the user is in the game
        await super().connect()
        # Add client to the channel layer group
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        logging.info(
            f"Opening WebSocket connection for game {self.game_id} and user {self.scope['user']} ...")

        # Set the player ready
        game = await database_sync_to_async(Game.objects.get)(id=self.game_id)
        game.set_player_ready(self.scope['user'].id, True)

        game_name = f"game_{self.game_id}"
        await channel_layer.group_add(game_name, self.channel_name)

        # Accept the connection
        await self.accept()

        can_start_game, start_time = await send_player_ready_state(game, channel_layer)

        logging.info(
            f"WebSocket connection for game {self.game_id} and user {self.scope['user']} opened.")
        if can_start_game:
            await init_game(game)
            GameConsumer.game_loops[self.game_id] = asyncio.create_task(
                GameConsumer.run_game_loop(self.game_id, start_time))

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Set the player ready to false
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        game = await sync_to_async(Game.objects.get)(id=self.game_id)
        game.set_player_ready(self.scope['user'].id, False)

        await send_player_ready_state(game, channel_layer)

        await update_game_state_db(game, Game.GameState.PAUSED)

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # Calling the receive function of the parent class (CustomWebSocketLogic)
        await super().receive(text_data)
        # Setting the user
        user = self.scope['user']
        # Process the message
        await WebSocketMessageHandlersGame()[f"{self.message_type}"](self, user, text_data)

    @barely_handle_ws_exceptions
    async def update_players_ready(self, event):
        await self.send(text_data=json.dumps({**event}))

    @barely_handle_ws_exceptions
    async def update_game_state(self, event):
        await self.send(text_data=json.dumps({**event}))

    @staticmethod
    async def run_game_loop(game_id, start_time):
        while True:
            try:
                # Fetches user desires from cache
                left_player_input = cache.get(f'game_{game_id}_player_left', {})
                right_player_input = cache.get(f'game_{game_id}_player_right', {})

                # Fetches game state from cache
                game_state_data = cache.get(f'game_{game_id}_state', {})

                # Extract user state from game state
                game_state_data_left = game_state_data['playerLeft']
                game_state_data_right = game_state_data['playerRight']

                # Change postions of both paddles if requested and allowed
                game_state_data_left = move_paddle(left_player_input, game_state_data_left)
                game_state_data_right = move_paddle(right_player_input, game_state_data_right)

                # Update game state with new paddle positions
                game_state_data['playerLeft'] = game_state_data_left
                game_state_data['playerRight'] = game_state_data_right

                # Then calculate ball movement
                game_state_data = move_ball(game_state_data)

                # Send the updated game state to FE
                game_name = f"game_{game_id}"
                await channel_layer.group_send(
                    game_name,
                    {
                        "type": "update_game_state",
                        "messageType": "gameState",
                        **game_state_data
                    }
                )

                # Store the updated game state in cache
                cache.set(f'game_{game_id}_state', game_state_data, timeout=3000)

                # Check if the game is over and exit the loop
                if game_state_data['gameData']['state'] == 'finished':
                    break

                # Await for next frame render
                await asyncio.sleep(1 / GAME_FPS)
            except Exception as e:
                logging.error(f"Error in game loop: {e}")
                break
        logging.info(f"Game finished: {game_id}")


def move_paddle(player, game_state_data_player):
    # logging.info(f"paddlePos for {player['movePaddle']}: {game_state_data_player['paddlePos']}")

    if player['movePaddle'] == '0':
        return game_state_data_player

    logging.info(f"player['movePaddle']: player['movePaddle']")

    new_paddle_pos = game_state_data_player['paddlePos']
    if player['movePaddle'] == '+':
        new_paddle_pos += game_state_data_player['paddleSpeed']
    elif player['movePaddle'] == '-':
        new_paddle_pos -= game_state_data_player['paddleSpeed']

    if (new_paddle_pos - (game_state_data_player['paddleSize'] / 2)) < 0:
        new_paddle_pos = game_state_data_player['paddleSize'] / 2

    elif (new_paddle_pos + (game_state_data_player['paddleSize'] / 2)) > 100:
        new_paddle_pos = 100 - (game_state_data_player['paddleSize'] / 2)
    game_state_data_player['paddlePos'] = new_paddle_pos
    return game_state_data_player


def move_ball(game_state_data):
    #logging.info(f"ballPos:\t x --> {game_state_data['gameData']['ballPosX']} \t y --> {game_state_data['gameData']['ballPosY']} \t Players pos: left --> {game_state_data['playerLeft']['paddlePos']} {game_state_data['playerRight']['paddlePos']}")

    # Move the ball
    game_state_data['gameData']['ballPosX'] += game_state_data['gameData']['ballDirectionX'] * game_state_data['gameData']['ballSpeed']
    game_state_data['gameData']['ballPosY'] += game_state_data['gameData']['ballDirectionY'] * game_state_data['gameData']['ballSpeed']

    # Check if the ball is hitting the left or right paddle(point was scored)
    if game_state_data['gameData']['ballPosX'] <= PADDLE_OFFSET + game_state_data['gameData']['ballRadius']:
        game_state_data['gameData']['ballPosX'] = PADDLE_OFFSET + game_state_data['gameData']['ballRadius']
        game_state_data['gameData']['ballDirectionX'] *= -1
        game_state_data = check_padlle_hit(game_state_data, 'playerLeft')
    elif game_state_data['gameData']['ballPosX'] >= 100 - PADDLE_OFFSET - game_state_data['gameData']['ballRadius']:
        game_state_data['gameData']['ballPosX'] = 100 - PADDLE_OFFSET - game_state_data['gameData']['ballRadius']
        game_state_data['gameData']['ballDirectionX'] *= -1
        game_state_data = check_padlle_hit(game_state_data, 'playerRight')

    # Calculate if the upper or lower wall was hit
    if game_state_data['gameData']['ballPosY'] <= game_state_data['gameData']['ballRadius']:
        game_state_data['gameData']['ballPosY'] = game_state_data['gameData']['ballRadius']
        game_state_data['gameData']['ballDirectionY'] *= -1
    elif game_state_data['gameData']['ballPosY'] >= 100 - game_state_data['gameData']['ballRadius']:
        game_state_data['gameData']['ballPosY'] = 100 - game_state_data['gameData']['ballRadius']
        game_state_data['gameData']['ballDirectionY'] *= -1

    return game_state_data

def check_padlle_hit(game_state_data, player_side):
    # Check if a point was scored
    # if ballPos < paddlePos
    if game_state_data['gameData']['ballPosY'] < game_state_data[player_side]['paddlePos']:
    #     if ballPos + ballRadius < paddlePos - paddleSize / 2
        if game_state_data['gameData']['ballPosY'] + game_state_data['gameData']['ballRadius'] < game_state_data[player_side]['paddlePos'] - game_state_data[player_side]['paddleSize'] / 2:
    #         score a point
            game_state_data = score_point(game_state_data, player_side)
        else:
            # Ball should bounce off up
    #         distance_paddle_ball = paddlePos - ballPos
            distance_paddle_ball = game_state_data[player_side]['paddlePos'] - game_state_data['gameData']['ballPosY']
    #         percentage_y = distance_paddle_ball / (paddleSize / 2 + ballRadius)
            percentage_y = distance_paddle_ball / (game_state_data[player_side]['paddleSize'] / 2 + game_state_data['gameData']['ballRadius'])
    #         ballDirectionY = -percentage_y
            game_state_data['gameData']['ballDirectionY'] = -percentage_y
    else:
    #     if ballPos - ballRadius > paddlePos + paddleSize / 2
        if game_state_data['gameData']['ballPosY'] - game_state_data['gameData']['ballRadius'] > game_state_data[player_side]['paddlePos'] + game_state_data[player_side]['paddleSize'] / 2:
    #         score a point
            game_state_data = score_point(game_state_data, player_side)
        else:
    #         # Ball should bounce off down
    #         distance_paddle_ball = ballPos - paddlePos
            distance_paddle_ball = game_state_data['gameData']['ballPosY'] - game_state_data[player_side]['paddlePos']
    #         percentage_y = distance_paddle_ball / (paddleSize / 2 + ballRadius)
            percentage_y = distance_paddle_ball / (game_state_data[player_side]['paddleSize'] / 2 + game_state_data['gameData']['ballRadius'])
    #         ballDirectionY = percentage_y
            game_state_data['gameData']['ballDirectionY'] = percentage_y

    return game_state_data


def score_point(game_state_data, player_side):
    game_state_data['gameData']['ballPosX'] = 50
    game_state_data['gameData']['ballPosY'] = 50
    game_state_data['gameData']['ballSpeed'] = 1

    if (game_state_data['gameData']['remainingServes'] > 0):
        game_state_data['gameData']['remainingServes'] -= 1
    else:
        game_state_data['gameData']['remainingServes'] = 2
        if (game_state_data['gameData']['playerServes'] == 'playerLeft'):
            game_state_data['gameData']['playerServes'] = 'playerRight'
        else:
            game_state_data['gameData']['playerServes'] = 'playerLeft'

    if (game_state_data['gameData']['playerServes'] == 'playerLeft'):
        game_state_data['gameData']['ballDirectionX'] = -1
    else:
        game_state_data['gameData']['ballDirectionX'] = 1
    # Setting dir to a random value
    game_state_data['gameData']['ballDirectionY'] = random.uniform(-0.01, 0.01)

    # Update the score
    if (player_side == 'playerLeft'):
        game_state_data['playerLeft']['points'] += 1 # TODO: HACKATHON Update db
    else:
        game_state_data['playerRight']['points'] += 1 # TODO: HACKATHON Update db

    if (game_state_data['playerLeft']['points'] >= 11 or game_state_data['playerRight']['points'] >= 11):
        game_state_data['gameData']['state'] = 'finished' # TODO: HACKATHON Update db

    return game_state_data
