GAME_FPS = 15
RECONNECT_TIMEOUT = 2 # Minutes
POWERUP_DURATION = 10 # Seconds
INIT_BALL_SPEED = 3

# TODO: This should be a percentage of the screen where the paddel hit surface is.
# It should be decieed in the render of the frontend game field and then set here.
PADDLE_OFFSET = 3

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
        "paddleSpeed": 1.5
    },
    "playerRight" : {
        "points": 0,
        "paddlePos": 50,
        "paddleSize": 10,
        "powerupBig": "unavailable",
        "powerupSlow": "unavailable",
        "powerupFast": "unavailable",
        "paddleSpeed": 1.5
    },
    "gameData" : {
        "ballPosX": 50,
        "ballPosY": 50,
        "state": "pending",
        "ballSpeed": INIT_BALL_SPEED,
        "ballRadius": 1,
        "ballDirectionX": -1,
        "ballDirectionY": 0,
        "playerServes": "playerLeft",
        "remainingServes": 2,
        "extendingGameMode": False
    }
}

