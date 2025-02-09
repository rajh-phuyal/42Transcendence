GAME_FPS = 15
RECONNECT_TIMEOUT = 2 # Minutes
POWERUP_DURATION = 10 # Seconds
INIT_BALL_SPEED = 3

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
    "activatePowerupSlow": False,
    "activatePowerupFast": False
}

GAME_STATE = {
    "playerLeft" : {
        "points": 0,
        "paddlePos": 50,
        "paddleSize": 10,
        "powerupBig": "unavailable",
        "powerupSlow": "unavailable",
        "powerupFast": "unavailable",
        "paddleSpeed": 2.5
    },
    "playerRight" : {
        "points": 0,
        "paddlePos": 50,
        "paddleSize": 10,
        "powerupBig": "unavailable",
        "powerupSlow": "unavailable",
        "powerupFast": "unavailable",
        "paddleSpeed": 2.5
    },
    "ball" : {
        "posX": 50,
        "posY": 50,
        "height": 1,
        "width": 1,
        "speed": INIT_BALL_SPEED,
        "directionX": -1,
        "directionY": 0
    },
    "gameData" : {
        "state": "pending",
        "playerServes": "playerLeft",
        "remainingServes": 2,
        "extendingGameMode": False,
        "sound": "none",
    }
}
