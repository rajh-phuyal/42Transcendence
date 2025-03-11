GAME_COUNTDOWN_MAX = 5 # Notice that the fe needs to have the countdown images for this to work
GAME_FPS = 15
RECONNECT_TIMEOUT = 2 # Minutes
INIT_BALL_SPEED = 1.5
BALL_SPEED_STEP = 0.1
INIT_PADDLE_SIZE = 10

MAPNAME_TO_MAPNUMBER = {
    "ufo": 1,
    "lizard-people": 2,
    "snowman": 3,
    "lochness": 4
}

# This should be a percentage of the screen where the paddel hit surface is.
# It should be decieed in the render of the frontend game field and then set here.
# The paddle is drawn 1% of the screen width and the paddle width is 1% of the screen width.
# NOTE: those values are hardcoded in the frontend objects.js "paddleWidth"
PADDLE_OFFSET = 4

GAME_PLAYER_INPUT = {
    "movePaddle": "0",
    "activatePowerupBig": False,
    "activatePowerupSpeed": False
}

GAME_STATE = {
    "playerLeft" : {
        "points": 0,
        "result": "pending",
        "paddlePos": 50,
        "paddleSize": INIT_PADDLE_SIZE,
        "powerupBig": "unavailable",
        "powerupSlow": "unavailable",
        "powerupFast": "unavailable",
        "paddleSpeed": 3.5
    },
    "playerRight" : {
        "points": 0,
        "result": "pending",
        "paddlePos": 50,
        "paddleSize": INIT_PADDLE_SIZE,
        "powerupBig": "unavailable",
        "powerupSlow": "unavailable",
        "powerupFast": "unavailable",
        "paddleSpeed": 3.5
    },
    "ball" : {
        "posX": 50,
        "posY": 50,
        "height": 1,
        "width": 1,
        "speed": INIT_BALL_SPEED,
        "lastSpeed": 0,
        "directionX": -1,
        "directionY": 0
    },
    "gameData" : {
        "state": "pending",
        "tournament": False,
        "playerServes": "playerLeft",
        "remainingServes": 2,
        "extendingGameMode": False,
        "sound": "none",
    }
}
