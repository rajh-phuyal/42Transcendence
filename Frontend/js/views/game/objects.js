export const gameObject = {
    /* NOTE: IF U ADD SOMETHING HERE WE ALSO NEED TO ADD IT TO initObjects() */
    gameId: undefined,
    countDownInterval: undefined,
    tournamentId: undefined,
    mapName: undefined,
    wsConnection: false,
    state: undefined,
    frameTime: 1000/25, // NOTE: this means 25 frames per second which should match the backend FPS
    lastFrameTime: 0,
    animationId: undefined,
    deadline: undefined,
    sound: undefined,
    paddleWidth: 1,     //  This means 1% of the game field width. If changed, also change the BE: PADDLE_OFFSET
    paddleSpacing: 2,   //  This means 1% of the game field width is keept as a distance btween wall and paddle. If changed, also change the BE: PADDLE_OFFSET
    borderStrokeWidth: 2,
    clientIsPlayer: false, // Since all users can watch the lobby, this is used to determine if the client is a player or a spectator
    playerInputLeft: {
        paddleMovement: 0,
        powerupSpeed: false,
        powerupBig: false,
    },
    playerInputRight: {
        paddleMovement: 0,
        powerupSpeed: false,
        powerupBig: false,
    },
    playerLeft: {
        id: undefined,
        state: undefined,
        points: 0,
        pos: 50,
        size: 10,
        result: undefined,
        powerupBig: "unavailable",
        powerupSlow: "unavailable",
        powerupFast: "unavailable"
    },
    playerRight: {
        id: undefined,
        state: undefined,
        points: 0,
        pos: 50,
        size: 10,
        result: undefined,
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
    keyStrokes:{
        w: undefined,
        s: undefined,
        o: undefined,
        l: undefined
    }
}
