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
    },
}
