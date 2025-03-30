# Basics
import logging, asyncio, json, math
from datetime import timedelta
from django.utils import timezone # Don't use from datetime import timezone, it will conflict with django timezone!
# Django
from django.utils.translation import gettext as _
# Core
from core.decorators import barely_handle_ws_exceptions
# User
from user.constants import USER_ID_AI
# Game stuff
from game.models import Game, GameMember
from game.constants import GAME_FPS, GAME_COUNTDOWN_MAX, RECONNECT_TIMEOUT
from game.AI import AIPlayer, calculate_ai_difficulty, difficulty_to_string
from game.utils import is_left_player, get_user_of_game
from game.utils_ws import update_game_state
from game.game_cache import get_game_data, set_game_data, init_game_on_cache, delete_game_from_cache, set_player_input
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
    ai_players = {}

    async def _load_game(self):
        self.game = await database_sync_to_async(
            # Prefetch the tournament and members to avoid lazy loading issues
            lambda: Game.objects.select_related("tournament").prefetch_related("members__user").get(id=self.game_id)
        )()

    async def _is_game_invalid(self):
        if self.game.state in [Game.GameState.FINISHED, Game.GameState.QUITED]:
            logging.info(f"WEBSOCKET GAME CONNECT: Game {self.game_id} is not in the right state to be played. CONNECTION CLOSED.")
            await self.close()
            return True
        return False

    async def _authorize_connection(self):
        # CHECK IF CLIENT IS ALLOWED TO CONNECT
        # We have two cases:
        #     NORMAL GAME:
        #       - game members:         connect as player
        #       - game non members:     connect as viewer
        #    LOCAL TOURNAMENT GAME:
        #       - tournament admin:     connect as player
        #       - tournament non admin: connect as viewer
        allowed = False
        tournament = self.game.tournament

        if tournament and tournament.local_tournament:
            logging.info(f"WEBSOCKET GAME CONNECT: Game {self.game_id} is part of a local tournament.")
            admin = await self._get_tournament_admin(tournament)
            if admin and admin.user_id == self.user.id:
                allowed = True
            else:
                logging.info(f"WEBSOCKET GAME CONNECT: User {self.user.id} is not tournament admin -> Viewer mode.")
        else:
            logging.info("WEBSOCKET GAME CONNECT: Normal game, checking if user is a member.")
            allowed = await self._is_game_member(self.user.id)

        if not allowed:
            self.isOnlyViewer = True
            await self._join_group()
            await self.accept()
            await send_ws_game_data_msg(self.game_id)
            return

    @database_sync_to_async
    def _is_game_member(self, user_id):
        return self.game.members.filter(user_id=user_id).exists()

    @database_sync_to_async
    def _get_tournament_admin(self, tournament):
        return tournament.members.filter(is_admin=True).first()

    async def _join_group(self):
        # Note: here i can't use update_client_in_group since this always uses the main ws connection!
        group_name = f"{PRE_GROUP_GAME}{self.game_id}"
        await channel_layer.group_add(group_name, self.channel_name)

    async def _init_player_state(self):
        self.isLeftPlayer   = await database_sync_to_async(is_left_player)(self.game_id, self.user.id)
        self.leftUser       = await database_sync_to_async(get_user_of_game)(self.game_id, 'playerLeft')
        self.rightUser      = await database_sync_to_async(get_user_of_game)(self.game_id, 'playerRight')
        self.leftMember     = await database_sync_to_async(GameMember.objects.get)(game=self.game, user=self.leftUser)
        self.rightMember    = await database_sync_to_async(GameMember.objects.get)(game=self.game, user=self.rightUser)

        await init_game_on_cache(self.game, self.leftMember, self.rightMember)
        await self.accept()
        await send_ws_game_data_msg(self.game_id)
        logging.info(f"WEBSOCKET GAME CONNECT: Game {self.game_id} - Left: {self.leftUser.id}, Right: {self.rightUser.id}")

    async def _set_ready_state(self):
        tournament = self.game.tournament
        if tournament and tournament.local_tournament:
            # local tournament game: set both players ready
            await database_sync_to_async(self.game.set_player_ready)(self.leftUser.id, True)
            await database_sync_to_async(self.game.set_player_ready)(self.rightUser.id, True)
        else:
            # normal game: set only the client ready
            await database_sync_to_async(self.game.set_player_ready)(self.user.id, True)

        left_ready  = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        # Send the player ready message and the game data to the group
        await send_ws_game_players_ready_msg(self.game_id, left_ready, right_ready)
        await send_ws_game_data_msg(self.game_id)

    async def _maybe_start_game_loop(self):
        # If both users are ready start the loop
        left_ready  = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        if left_ready and right_ready:
            try:
                # here we can asume the left user is not the AI, when game with ai since the AI is always the right player (lower id)
                if self.game_id not in self.ai_players and self.rightUser.id == USER_ID_AI:
                    logging.info(f"WEBSOCKET GAME CONNECT: AI player added to game: {self.game_id}")
                    # calculate the difficulty (we need to start the ai with some difficulty if mid game)
                    ai_score     = get_game_data(self.game_id, 'playerRight', 'points') or 0
                    player_score = get_game_data(self.game_id, 'playerLeft',  'points') or 0
                    difficulty = calculate_ai_difficulty(ai_score, player_score)
                    logging.info(f"WEBSOCKET GAME CONNECT: Starting AI difficulty: {difficulty_to_string(difficulty)}")
                    self.ai_players[self.game_id] = {
                        "stateSnapshotAt": timezone.now(),
                        "player": AIPlayer(difficulty=difficulty, game_id=self.game_id),
                        "side": "playerRight"
                    }
            except Exception as e:
                logging.error(f"WEBSOCKET GAME CONNECT: Error initializing AI player: {e}")

            asyncio.create_task(self.start_the_game())

    @barely_handle_ws_exceptions
    async def connect(self):
        # Future Improvement: check if the user is already connected to the game to prevent multiple connections
        await super().connect()
        # Set self vars for consumer
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.isOnlyViewer = False

        await self._load_game()
        if await self._is_game_invalid():
            return

        await self._authorize_connection()
        if self.isOnlyViewer:
            return  # Viewer was already accepted and handled

        await self._join_group()
        await self._init_player_state()
        await self._set_ready_state()
        await self._maybe_start_game_loop()
        return

    @barely_handle_ws_exceptions
    async def disconnect(self, close_code):
        await super().disconnect(close_code)
        # Remove client from the channel layer group
        # Note: here i can't use update_client_in_group since this always uses the main ws connection!
        group_name = f"{PRE_GROUP_GAME}{self.game_id}"
        await channel_layer.group_discard(group_name, self.channel_name)

        # If the client is only a viewer return
        if self.isOnlyViewer:
            return

        # Set the player NOT ready
        self.game.set_player_ready(self.user.id, False)
        left_ready = await database_sync_to_async(self.game.get_player_ready)(self.leftUser.id)
        right_ready = await database_sync_to_async(self.game.get_player_ready)(self.rightUser.id)
        await send_ws_game_players_ready_msg(self.game_id, left_ready, right_ready)
        # If the game was ongoing, pause it
        if get_game_data(self.game_id, 'gameData', 'state') == Game.GameState.ONGOING or get_game_data(self.game_id, 'gameData', 'state') == Game.GameState.COUNTDOWN:
            # Set the deadline to reconnection time
            new_deadline = timezone.now() + RECONNECT_TIMEOUT
            await database_sync_to_async(lambda: setattr(self.game, 'deadline', new_deadline))()
            await database_sync_to_async(self.game.save)()
            # logging.info(f"Game {self.game_id} was paused because of a disconnect with timestamp: {self.game.deadline}")
            set_game_data(self.game_id, 'gameData', 'deadline', new_deadline)
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

        # Clean up AI player if it exists
        if self.game_id in self.ai_players:
            self.ai_players[self.game_id]['player'].cleanup()
            del self.ai_players[self.game_id]

    @barely_handle_ws_exceptions
    async def receive(self, text_data):
        # If the client is only a viewer return
        if self.isOnlyViewer:
            return

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
        start_time = timezone.now() + timedelta(seconds=GAME_COUNTDOWN_MAX)
        start_time_formated = start_time.isoformat()
        logging.info(f"Game will start at: {start_time_formated}")
        await send_ws_game_players_ready_msg(self.game_id, True, True, start_time_formated)
        # Updates the state to countdown
        await update_game_state(self.game_id, Game.GameState.COUNTDOWN)
        await send_ws_game_data_msg(self.game_id)
        # 2. Calculate the delay so the game loop start not before the start time
        delay = (start_time - timezone.now()).total_seconds()
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
    async def ai_action(game_id):
        if game_id not in GameConsumer.ai_players:
            return None

        game_ai = GameConsumer.ai_players[game_id]
        ai = game_ai['player']
        ai_side = game_ai['side']  # Get the side the AI is playing on
        last_state_snapshot_at = game_ai['stateSnapshotAt']

        try:
            # Update AI with fresh game state once per second
            if (timezone.now() - last_state_snapshot_at).total_seconds() > 1:
                game_ai['stateSnapshotAt'] = timezone.now()

                # Get complete game state for the AI to make better decisions
                game_state = {
                    'gameData': get_game_data(game_id, 'gameData'),
                    'ball': get_game_data(game_id, 'ball'),
                    'playerLeft': get_game_data(game_id, 'playerLeft'),
                    'playerRight': get_game_data(game_id, 'playerRight')
                }

                ai.update(game_state)

            # Get the next action from AI - with proper await
            action = await ai.action()

            # Apply the action to the game
            if action and isinstance(action, dict):
                set_player_input(game_id, ai_side, action)
                return

            raise Exception("Invalid AI action")

        except Exception as e:
            logging.error(f"Error managing AI for game {game_id}: {e}")
            # In case of error, use a default "do nothing" action
            default_action = {
                'movePaddle': "0",
                'activatePowerupBig': False,
                'activatePowerupSpeed': False
            }
            set_player_input(game_id, ai_side, default_action)

    @staticmethod
    async def run_game_loop(game_id):
        # Start the game loop
        logging.info(f"Game loop starts now: {game_id}")
        # Set state to ongoing
        await update_game_state(game_id, Game.GameState.ONGOING)
        while get_game_data(game_id, 'gameData', 'state') == 'ongoing':
            try:
                # Process AI input if this game has an AI player
                if game_id in GameConsumer.ai_players:
                    await GameConsumer.ai_action(game_id)

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
