export const gameObject ={
        state: undefined,
        lastFrameTime: undefined,
        animationId: undefined,
        playerInput: {
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