import logging, random
from game.constants import PADDLE_OFFSET, INIT_BALL_SPEED
from game.models import Game
from game.utils import is_left_player, get_game_data, set_game_data, get_player_input, get_user_of_game
from game.utils_ws import update_game_state, update_game_points

# Player side needs to be 'playerLeft' or 'playerRight'
async def activate_power_ups(game_id, playerSide):
    # TODO Implement Powerups issue #308
    # I guess it should be done by just changeing the game state data on cache
    # The calculation of ball move and paddle move should be done with the new game state data
    if get_player_input(game_id, playerSide, 'activatePowerupBig') == 'true':
        logging.info(f"PowerUp BIG tried to activate by: {playerSide}")
    if get_player_input(game_id, playerSide, 'activatePowerupSlow') == 'true':
        logging.info(f"PowerUp SLOW tried to activate by: {playerSide}")
    if get_player_input(game_id, playerSide, 'activatePowerupFast') == 'true':
        logging.info(f"PowerUp FAST tried to activate by: {playerSide}")

# Player side needs to be 'playerLeft' or 'playerRight'
async def move_paddle(game_id, playerSide):
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

async def move_ball(game_id):

    # Get from cache
    ball_pos_x = get_game_data(game_id, 'gameData', 'ballPosX')
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    ball_direction_x = get_game_data(game_id, 'gameData', 'ballDirectionX')
    ball_direction_y = get_game_data(game_id, 'gameData', 'ballDirectionY')
    ball_speed = get_game_data(game_id, 'gameData', 'ballSpeed')

    # Move the ball
    ball_pos_x += ball_direction_x * ball_speed
    ball_pos_y += ball_direction_y * ball_speed
    # TODO: change ball speed issue #311

    # Save the new ball position
    set_game_data(game_id, 'gameData', 'ballPosX', ball_pos_x)
    set_game_data(game_id, 'gameData', 'ballPosY', ball_pos_y)

async def apply_wall_bonce(game_id):
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    ball_direction_y = get_game_data(game_id, 'gameData', 'ballDirectionY')
    # Apply wall bounce (Calculate if the upper or lower wall was hit)
    if ball_pos_y <= ball_radius:
        set_game_data(game_id, 'gameData', 'ballPosY', ball_radius)
        set_game_data(game_id, 'gameData', 'ballDirectionY', ball_direction_y * -1)
        set_game_data(game_id, 'gameData', 'sound', 'wall')
    elif ball_pos_y >= 100 - ball_radius:
        set_game_data(game_id, 'gameData', 'ballPosY', 100 - ball_radius)
        set_game_data(game_id, 'gameData', 'ballDirectionY', ball_direction_y * -1)
        set_game_data(game_id, 'gameData', 'sound', 'wall')
    else:
        # No wall bounce happend
        ...

async def check_paddle_bounce(game_id):
    ball_pos_x = get_game_data(game_id, 'gameData', 'ballPosX')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')

    # Check if the ball is hitting the left or right paddle(point was scored)
    if ball_pos_x <= PADDLE_OFFSET + ball_radius:
        await apply_padlle_hit(game_id, 'playerLeft')
    elif ball_pos_x >= 100 - PADDLE_OFFSET - ball_radius:
        await apply_padlle_hit(game_id, 'playerRight')
    else:
        # No paddle bounce happend
        ...

# Only called when the x pos of ball is on the x of the paddle
# TODO: In this function we need to normalize the ball direction so the speed is always the same issue #311
async def apply_padlle_hit(game_id, player_side):
    ball_pos_y = get_game_data(game_id, 'gameData', 'ballPosY')
    paddle_pos = get_game_data(game_id, player_side, 'paddlePos')
    paddle_size = get_game_data(game_id, player_side, 'paddleSize')
    ball_radius = get_game_data(game_id, 'gameData', 'ballRadius')
    # logging.info(f"Ball pos y: {ball_pos_y}, paddle pos: {paddle_pos}, paddle size: {paddle_size}")

    # Check if a point was scored
    if ball_pos_y < paddle_pos:
        if ball_pos_y + ball_radius < paddle_pos - paddle_size / 2:
            await apply_point(game_id, player_side)
        else:
            # Ball should bounce off up
            distance_paddle_ball = paddle_pos - ball_pos_y
            percentage_y = distance_paddle_ball / (paddle_size / 2 + ball_radius)
            set_game_data(game_id, 'gameData', 'ballDirectionX', -1 * get_game_data(game_id, 'gameData', 'ballDirectionX'))
            set_game_data(game_id, 'gameData', 'ballDirectionY', -percentage_y)
            set_game_data(game_id, 'gameData', 'sound', 'paddle')
    else:
        if ball_pos_y - ball_radius > paddle_pos + paddle_size / 2:
            await apply_point(game_id, player_side)
        else:
            # Ball should bounce off down
            distance_paddle_ball = ball_pos_y - paddle_pos
            percentage_y = distance_paddle_ball / (paddle_size / 2 + ball_radius)
            set_game_data(game_id, 'gameData', 'ballDirectionX', -1 * get_game_data(game_id, 'gameData', 'ballDirectionX'))
            set_game_data(game_id, 'gameData', 'ballDirectionY', percentage_y)
            set_game_data(game_id, 'gameData', 'sound', 'paddle')

async def apply_point(game_id, player_side):
    # update_score_points in cache and db
    await update_game_points(game_id, player_side=player_side)
    set_game_data(game_id, 'gameData', 'sound', 'score')

    # Reset the ball
    set_game_data(game_id, 'gameData', 'ballPosX', 50)
    set_game_data(game_id, 'gameData', 'ballPosY', 50)
    set_game_data(game_id, 'gameData', 'ballSpeed', INIT_BALL_SPEED)
    set_game_data(game_id, 'gameData', 'ballDirectionY', random.uniform(-0.01, 0.01))
    # Reset the paddles
    set_game_data(game_id, 'playerLeft', 'paddlePos', 50)
    set_game_data(game_id, 'playerRight', 'paddlePos', 50)

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


async def check_if_game_is_finished(game_id):
    score_left = get_game_data(game_id, 'playerLeft', 'points')
    score_right = get_game_data(game_id, 'playerRight', 'points')
    if get_game_data(game_id, 'gameData', 'extendingGameMode'):
        # One player needs to points ahead
        if abs(score_left - score_right) >= 2:
            await update_game_state(game_id, Game.GameState.FINISHED)
            set_game_data(game_id, 'gameData', 'sound', 'gameover')
    else:
        # One player needs to score 11 points
        if score_left >= 11 or score_right >= 11:
            await update_game_state(game_id, Game.GameState.FINISHED)
            set_game_data(game_id, 'gameData', 'sound', 'gameover')
