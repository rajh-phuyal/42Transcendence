export const gameObject = {
    gameId: undefined,
    wsConnection: false,
    state: undefined,
    frameTime: undefined,
    lastFrameTime: undefined,
    animationId: undefined,
    sound: undefined,
    paddleWidth: 1, //  This means 1% of the game field width. If changed, also change the BE: PADDLE_OFFSET
    paddleSpacing: 2, //  This means 1% of the game field width is keept as a distance btween wall and paddle. If changed, also change the BE: PADDLE_OFFSET
    borderStrokeWidth: 2,
    playerInputLeft: {
        paddleMovement: undefined,
        powerupSpeed: undefined,
        powerupBig: undefined,
    },
    playerInputRight: {
        paddleMovement: undefined,
        powerupSpeed: undefined,
        powerupBig: undefined,
    },
    playerLeft: {
        state: undefined,
        points: undefined,
        pos: undefined,
        size: undefined,
        powerupBig: "unavailable",
        powerupSlow: "unavailable",
        powerupFast: "unavailable"
    },
    playerRight: {
        state: undefined,
        points: undefined,
        pos: undefined,
        size: undefined,
        powerupBig: "unavailable",
        powerupSlow: "unavailable",
        powerupFast: "unavailable"
    },
    ball: {
        posX: 50,
        posY: 50,
        height: 1,
        width: 1
    }
}
