GAME_FPS = 15

GAME_STATE = {
    "playerLeft" : {
        "points": 0,
        "paddlePos": 50,
        "paddleSize": 10,
        "powerupBig": 0,
        "powerupSlow": 0,
        "powerupFast": 0,
        "paddleSpeed": 1
    },
    "playerRight" : {
        "points": 0,
        "paddlePos": 50,
        "paddleSize": 10,
        "powerupBig": 0,
        "powerupSlow": 0,
        "powerupFast": 0,
        "paddleSpeed": 1
    },
    "gameData" : {
        "localGame": False,
        "ballPosX": 50,
        "ballPosY": 50,
        "state": "ongoing",
        "ballSpeed": 1,
        "ballRadius": 1,
        "ballDirectionX": -1,
        "ballDirectionY": 0,
        "playerServes": "playerLeft",
        "remainingServes": 2
    }
}

GAME_PLAYER_INPUT = {
    "movePaddle": "0",
    "activatePowerupBig": False,
    "activatePowerupSlow": False,
    "activatePowerupFast": False
}

PADDLE_OFFSET = 3
