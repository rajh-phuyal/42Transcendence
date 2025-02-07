export const gameObject = {
    gameId: undefined,
    wsConnection: false,
    state: undefined,
    frameTime: undefined,
    lastFrameTime: undefined,
    animationId: undefined,
    playMusic: true,
    playSounds: true,
    sound: undefined,
    playerInputLeft: {
        paddleMovement: undefined,
        powerupFast: undefined,
        powerupSlow: undefined,
        powerupBig: undefined,
    },
    playerInputRight: {
        paddleMovement: undefined,
        powerupFast: undefined,
        powerupSlow: undefined,
        powerupBig: undefined,
    },
    playerLeft: {
        points: undefined,
        pos: undefined,
        size: undefined,
        powerups: {
            big: undefined,
            slow: undefined,
            fast: undefined,
        }
    },
    playerRight: {
        points: undefined,
        pos: undefined,
        size: undefined,
        powerups: {
            big: undefined,
            slow: undefined,
            fast: undefined,
        }
    },
    ball: {
        posX: undefined,
        posY: undefined,
    },
}
