import logging, json
from django.core.cache import cache
from chat.utils_ws import process_incoming_chat_message, process_incoming_seen_message
from services.chat_service import broadcast_message
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.exceptions import BarelyAnException
from django.utils.translation import gettext as _
from datetime import datetime, timedelta
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from game.models import Game
from game.utils_ws import init_game, update_game_state_db

class WebSocketMessageHandlersMain:

    """If u wanna handle a new message type, add a new static method with the name handle_{message_type}"""
    def __getitem__(self, key):
        method_name = f"handle_{key}"

        # Use getattr to fetch the static method
        method = getattr(self, method_name, None)

        # If the method exists, return it, otherwise raise an error
        if callable(method):
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no method '{method_name}'")

    @staticmethod
    async def handle_chat(consumer, user, message):
        message = await process_incoming_chat_message(consumer, user, message)
        logging.info(f"Parsed backend object: {message}")
        await broadcast_message(message)

    @staticmethod
    async def handle_seen(consumer, user, message):
        logging.info("Received seen message")
        await process_incoming_seen_message(consumer, user, message)

    @staticmethod
    async def handle_relationship(consumer, user, message):
        logging.info("Received relationship message - TODO: issue #206 implement")

class WebSocketMessageHandlersGame:

    """If u wanna handle a new message type, add a new static method with the name handle_{message_type}"""
    def __getitem__(self, key):
        method_name = f"handle_{key}"

        # Use getattr to fetch the static method
        method = getattr(self, method_name, None)

        # If the method exists, return it, otherwise raise an error
        if callable(method):
            return method
        raise AttributeError(f"'{self.__class__.__name__}' object has no method '{method_name}'")

    @staticmethod
    async def handle_game(consumer, user, message):
        ...
        logging.info(f"Hanlding game message: {message}. tbd!")

    @staticmethod
    async def handle_playerInput(consumer, user, message):
        message = parse_message(message) # TODO: @Rajh implement deep json thing
        #logging.info(f"Handling player input message: {message} with game id {consumer.game_id}")

        # Validate that the user is allowed to send the data
        # Only if not local game we have to be strict with the player input
        game_state_data = cache.get(f'game_{consumer.game_id}_state', {})
        if not game_state_data:
            logging.info(f"Game state not found for game {consumer.game_id}")
            return
        local_game = game_state_data['gameData']['localGame']
        game = await database_sync_to_async(lambda: Game.objects.get(id=consumer.game_id))()
        game_user_ids = await database_sync_to_async(lambda: [player.user.id for player in list(game.game_members.all())])()
        player_right = await sync_to_async(game.get_player_ready)(min(game_user_ids))
        player_left = await sync_to_async(game.get_player_ready)(max(game_user_ids))

        # So if its a local game or the user matches the player, we can update the player input
        if local_game or player_right.user.id == consumer.user.id:
            if "playerRight" in message:
                cache.set(f'game_{consumer.game_id}_player_right', message["playerRight"], timeout=3000)
        if local_game or player_left.user.id == consumer.user.id:
            if "playerLeft" in message:
                cache.set(f'game_{consumer.game_id}_player_left', message["playerLeft"], timeout=3000)


async def check_if_game_can_be_started(game, channel_layer):
    game_user_ids = await database_sync_to_async(lambda: [player.user.id for player in list(game.game_members.all())])()
    player_right = await sync_to_async(game.get_player_ready)(min(game_user_ids))
    player_left = await sync_to_async(game.get_player_ready)(max(game_user_ids))
    start_time = None
    if player_left and player_right:
        # We can start the game
        # Step 1: Prepare the backend for starting the game
        try:
            await init_game(game)
        except BarelyAnException as e:
            logging.error(f"Error initializing game: {str(e)}")
            logging.info(f"TODO: remove this: but for debuging purposes we will set the state to pending. So if u try again, it will start...")
            await update_game_state_db(game, Game.GameState.PENDING)
            return False

        # STEP 2: Define the start time (so the frontend can start the game loop)
        start_time = datetime.now() + timedelta(seconds=5)
        start_time = start_time.isoformat()

    # STEP 3: Send the start game message to the frontend
    await send_update_players_ready_msg(game, channel_layer, start_time)

    return True if start_time else False

# To send by consumer
async def send_response_message(client_consumer, type, message):
    """Send a message to a WebSocket connection."""
    # logging.info(f"Sending message to connection {client_consumer}: {message}")
    message_dict = {
        "messageType": type,
        "message": message
    }
    json_message = json.dumps(message_dict)
    await client_consumer.send(text_data=json_message)

# To send by user id
async def send_message_to_user(user_id, **message):
    channel_name =  cache.get(f'user_channel_{user_id}', None)
    if channel_name:
        channel_layer = get_channel_layer()
        # Send the message to the WebSocket connection associated with that channel name
        await channel_layer.send(channel_name, message)
    else:
        logging.warning(f"No active WebSocket connection found for user ID {user_id}.")

@async_to_sync
async def send_message_to_user_sync(user_id, **message):
    await send_message_to_user(user_id, **message)

# For all incoming messages we should use this function to parse the message
# therefore we can validate if the message has all the required fields
# and if not, raise an exception
def parse_message(text: str, mandatory_keys: list[str] = None) -> dict:
    _message = json.loads(text)

    message_type = _message.get('messageType', None)
    if not message_type:
        raise BarelyAnException(_("messageType is required"))

    if not mandatory_keys:
        return _message

    for key in mandatory_keys:
        if key not in _message:
            raise BarelyAnException(_("key '{key}' is required in message type '{message_type}'").format(key=key, message_type=message_type))

    return _message
