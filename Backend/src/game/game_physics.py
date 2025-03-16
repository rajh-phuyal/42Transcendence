import logging, random, math
from game.constants import INIT_BALL_SPEED, BALL_SPEED_STEP, INIT_PADDLE_SIZE, PADDLE_OFFSET
from game.models import Game
from game.game_cache import get_game_data, set_game_data, get_player_input
from game.utils_ws import update_game_state, update_game_points, update_player_powerup

# Player side needs to be 'playerLeft' or 'playerRight'
async def activate_power_ups(game_id, player_side):
    if get_player_input(game_id, player_side, 'activatePowerupBig') == True:
        if await update_player_powerup(game_id, player_side, 'powerupBig', 'using'):
            set_game_data(game_id, player_side, 'paddleSize', 22)
    # to prevent both users activating a powerup at the same time
    if get_game_data(game_id, 'ball', 'lastSpeed') == 0:
        if get_player_input(game_id, player_side, 'activatePowerupSpeed') == True:
            if (player_side == 'playerLeft' and get_game_data(game_id, 'ball', 'directionX') < 0) or \
                (player_side == 'playerRight' and get_game_data(game_id, 'ball', 'directionX') >= 0):
                # the ball is moving towards the player: activate powerup SLOW
                if await update_player_powerup(game_id, player_side, 'powerupSlow', 'using'):
                    set_game_data(game_id, 'ball', 'lastSpeed', get_game_data(game_id, 'ball', 'speed'))
                    set_game_data(game_id, 'ball', 'speed', 1)
            else:
                # the ball is moving away from the player: activate powerup FAST
                if await update_player_powerup(game_id, player_side, 'powerupFast', 'using'):
                    set_game_data(game_id, 'ball', 'lastSpeed', get_game_data(game_id, 'ball', 'speed'))
                    set_game_data(game_id, 'ball', 'speed', get_game_data(game_id, 'ball', 'speed') + 2)

# Player side needs to be 'playerLeft' or 'playerRight'
async def move_paddle(game_id, player_side):
    movePaddle = get_player_input(game_id, player_side, 'movePaddle')
    if  movePaddle == '0':
        return

    new_paddle_pos = get_game_data(game_id, player_side, 'paddlePos')
    paddle_speed = get_game_data(game_id, player_side, 'paddleSpeed')
    paddle_size = get_game_data(game_id, player_side, 'paddleSize')

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
    set_game_data(game_id, player_side, 'paddlePos', new_paddle_pos)

async def move_ball(game_id):

    # Get from cache
    ball_pos_x = get_game_data(game_id, 'ball', 'posX')
    ball_pos_y = get_game_data(game_id, 'ball', 'posY')
    ball_direction_x = get_game_data(game_id, 'ball', 'directionX')
    ball_direction_y = get_game_data(game_id, 'ball', 'directionY')
    ball_speed = get_game_data(game_id, 'ball', 'speed')

    # Move the ball
    ball_pos_x += ball_direction_x * ball_speed
    ball_pos_y += ball_direction_y * ball_speed

    # Save the new ball position
    set_game_data(game_id, 'ball', 'posX', ball_pos_x)
    set_game_data(game_id, 'ball', 'posY', ball_pos_y)

async def apply_wall_bonce(game_id):
    ball_pos_y = get_game_data(game_id, 'ball', 'posY')
    ball_height = get_game_data(game_id, 'ball', 'height')
    ball_direction_y = get_game_data(game_id, 'ball', 'directionY')
    # Apply wall bounce (Calculate if the upper or lower wall was hit)
    if ball_pos_y <= ball_height:
        set_game_data(game_id, 'ball', 'posY', ball_height)
        set_game_data(game_id, 'ball', 'directionY', ball_direction_y * -1)
        set_game_data(game_id, 'gameData', 'sound', 'wall')
    elif ball_pos_y >= 100 - ball_height:
        set_game_data(game_id, 'ball', 'posY', 100 - ball_height)
        set_game_data(game_id, 'ball', 'directionY', ball_direction_y * -1)
        set_game_data(game_id, 'gameData', 'sound', 'wall')
    else:
        # No wall bounce happend
        ...

async def check_paddle_bounce(game_id):
    ball_pos_x = get_game_data(game_id, 'ball', 'posX')
    ball_prev_x = ball_pos_x - (get_game_data(game_id, 'ball', 'directionX') * get_game_data(game_id, 'ball', 'speed'))
    ball_width = get_game_data(game_id, 'ball', 'width')

    left_paddle_x = PADDLE_OFFSET + ball_width
    right_paddle_x = 100 - PADDLE_OFFSET - ball_width

    # Check for continuous collision with the left paddle
    if (ball_pos_x <= left_paddle_x and ball_prev_x > left_paddle_x) or ball_pos_x == left_paddle_x:
        # Ball crossed or exactly at the left paddle's x position
        await apply_padlle_hit(game_id, 'playerLeft')
    # Check for continuous collision with the right paddle
    elif (ball_pos_x >= right_paddle_x and ball_prev_x < right_paddle_x) or ball_pos_x == right_paddle_x:
        # Ball crossed or exactly at the right paddle's x position
        await apply_padlle_hit(game_id, 'playerRight')
    else:
        # No paddle bounce happened
        ...

async def normalize_ball_direction(new_dir_x, new_dir_y):
    magnitude = math.sqrt(new_dir_x ** 2 + new_dir_y ** 2)
    if magnitude != 0:
        new_dir_x /= magnitude
        new_dir_y /= magnitude
    return new_dir_x, new_dir_y

# Only called when the x pos of ball is on the x of the paddle
async def apply_padlle_hit(game_id, player_side):
    ball_pos_y = get_game_data(game_id, 'ball', 'posY')
    paddle_pos = get_game_data(game_id, player_side, 'paddlePos')
    paddle_size = get_game_data(game_id, player_side, 'paddleSize')
    ball_height = get_game_data(game_id, 'ball', 'height')
    # Add a small margin of error for more forgiving collisions (0.5% of game height)
    collision_margin = 0.5

    # logging.info(f"Ball pos y: {ball_pos_y}, paddle pos: {paddle_pos}, paddle size: {paddle_size}")

    # Check if a point was scored
    if ball_pos_y < paddle_pos:
        if ball_pos_y + ball_height + collision_margin < paddle_pos - paddle_size / 2:
            await apply_point(game_id, player_side)
        else:
            # Ball should bounce off up
            distance_paddle_ball = paddle_pos - ball_pos_y
            new_dir_y = -(distance_paddle_ball / (paddle_size / 2 + ball_height))
            new_dir_x = -1 * get_game_data(game_id, 'ball', 'directionX')
            new_dir_x, new_dir_y = await normalize_ball_direction(new_dir_x, new_dir_y)
            set_game_data(game_id, 'ball', 'directionX', new_dir_x)
            set_game_data(game_id, 'ball', 'directionY', new_dir_y)
            set_game_data(game_id, 'gameData', 'sound', 'paddle')
    else:
        if ball_pos_y - ball_height - collision_margin > paddle_pos + paddle_size / 2:
            logging.debug(f"Point scored: Ball below paddle - Ball y-height ({ball_pos_y - ball_height}) > paddle bottom ({paddle_pos + paddle_size / 2})")
            await apply_point(game_id, player_side)
        else:
            # Ball should bounce off down
            distance_paddle_ball = ball_pos_y - paddle_pos
            new_dir_y = distance_paddle_ball / (paddle_size / 2 + ball_height)
            new_dir_x = -1 * get_game_data(game_id, 'ball', 'directionX')
            new_dir_x, new_dir_y = await normalize_ball_direction(new_dir_x, new_dir_y)
            set_game_data(game_id, 'ball', 'directionX', new_dir_x)
            set_game_data(game_id, 'ball', 'directionY', new_dir_y)
            set_game_data(game_id, 'gameData', 'sound', 'paddle')
    # if power up BIG is active, decrease the size of the paddle
    current_paddle_size = get_game_data(game_id, player_side, 'paddleSize')
    if (current_paddle_size > INIT_PADDLE_SIZE):
        current_paddle_size -= 4
        if (current_paddle_size <= INIT_PADDLE_SIZE):
            await update_player_powerup(game_id, player_side, 'powerupBig', 'used')
            current_paddle_size = INIT_PADDLE_SIZE
        set_game_data(game_id, player_side, 'paddleSize', current_paddle_size)
    # speed up the ball or reset power up SLOW and FAST
    last_speed_ball = get_game_data(game_id, 'ball', 'lastSpeed')
    if (last_speed_ball > 0):
        set_game_data(game_id, 'ball', 'speed', last_speed_ball)
        set_game_data(game_id, 'ball', 'lastSpeed', 0)
        # We don't need to check here since update_player_powerup will only deactivate the powerup if it is active
        await update_player_powerup(game_id, 'playerLeft', 'powerupSlow', 'used')
        await update_player_powerup(game_id, 'playerLeft', 'powerupFast', 'used')
        await update_player_powerup(game_id, 'playerRight', 'powerupSlow', 'used')
        await update_player_powerup(game_id, 'playerRight', 'powerupFast', 'used')
    else:
        current_ball_speed = get_game_data(game_id, 'ball', 'speed')
        current_ball_speed += BALL_SPEED_STEP
        set_game_data(game_id, 'ball', 'speed', current_ball_speed)

async def apply_point(game_id, player_side):
    # update_score_points in cache and db
    # If the side is left, the right player scored
    if player_side == 'playerLeft':
        await update_game_points(game_id, player_side='playerRight')
    else:
        await update_game_points(game_id, player_side='playerLeft')
    set_game_data(game_id, 'gameData', 'sound', 'score')
    # Reset the paddles
    set_game_data(game_id, 'playerLeft', 'paddlePos', 50)
    set_game_data(game_id, 'playerRight', 'paddlePos', 50)
    set_game_data(game_id, 'playerLeft', 'paddleSize', INIT_PADDLE_SIZE)
    set_game_data(game_id, 'playerRight', 'paddleSize', INIT_PADDLE_SIZE)

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
    # Reset the ball
    # X: Direction & Postion depends on the serving player
    if get_game_data(game_id, 'gameData', 'playerServes') == 'playerLeft':
        set_game_data(game_id, 'ball', 'directionX', 1)
        set_game_data(game_id, 'ball', 'posX', PADDLE_OFFSET)
    else:
        set_game_data(game_id, 'ball', 'directionX', -1)
        set_game_data(game_id, 'ball', 'posX', 100 - PADDLE_OFFSET)
    # Y: Random direction (to avoid the same ball movement and stuck in a loop)
    set_game_data(game_id, 'ball', 'directionY', random.uniform(-0.01, 0.01))
    set_game_data(game_id, 'ball', 'posY', 50)
    # Speed: Reset to initial speed
    set_game_data(game_id, 'ball', 'speed', INIT_BALL_SPEED)
    # Reset all powerups
    set_game_data(game_id, 'ball', 'lastSpeed', 0)
    await update_player_powerup(game_id, 'playerLeft', 'powerupBig', 'used')
    await update_player_powerup(game_id, 'playerLeft', 'powerupFast', 'used')
    await update_player_powerup(game_id, 'playerLeft', 'powerupSlow', 'used')
    await update_player_powerup(game_id, 'playerRight', 'powerupBig', 'used')
    await update_player_powerup(game_id, 'playerRight', 'powerupFast', 'used')
    await update_player_powerup(game_id, 'playerRight', 'powerupSlow', 'used')

async def check_if_game_is_finished(game_id):
    score_left = get_game_data(game_id, 'playerLeft', 'points')
    score_right = get_game_data(game_id, 'playerRight', 'points')
    if get_game_data(game_id, 'gameData', 'extendingGameMode'):
        # One player needs to points ahead
        if abs(score_left - score_right) >= 2:
            await update_game_state(game_id, Game.GameState.FINISHED)
    else:
        # One player needs to score 11 points
        if score_left >= 11 or score_right >= 11:
            await update_game_state(game_id, Game.GameState.FINISHED)
