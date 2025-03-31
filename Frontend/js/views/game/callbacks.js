import { gameObject } from "./objects.js";

export function keyPressCallback(event) {
    switch (event.key) {
        // Player LEFT
        case "w":
            if (!gameObject.playerInputLeft.paddleMovement) { // to prevent unpredictable pedal movement if the game with a key press already
                gameObject.playerInputLeft.paddleMovement = -1;
                return ;
            }
            // Move the paddle up
            gameObject.playerInputLeft.paddleMovement--;
            if (gameObject.playerInputLeft.paddleMovement < -1)
                gameObject.playerInputLeft.paddleMovement = -1;
            break;
        case "s":
            if (!gameObject.playerInputLeft.paddleMovement) {
                gameObject.playerInputLeft.paddleMovement = 1;
                return ;
            }
                // Move the paddle down
            gameObject.playerInputLeft.paddleMovement++;
            if (gameObject.playerInputLeft.paddleMovement > 1)
                gameObject.playerInputLeft.paddleMovement = 1;
            break;
        case "1":
            // Activate the powerup
            gameObject.playerInputLeft.powerupBig = true;
            break;
        case "2":
            // Activate the powerup
            gameObject.playerInputLeft.powerupSpeed = true;
            break;

        // Player RIGHT
        case "o":
            if (!gameObject.playerInputRight.paddleMovement) {
                gameObject.playerInputRight.paddleMovement = -1;
                return ;
            }
            gameObject.playerInputRight.paddleMovement--;
            if (gameObject.playerInputRight.paddleMovement < -1)
                gameObject.playerInputRight.paddleMovement = -1;
            break;
        case "l":
            if (!gameObject.playerInputRight.paddleMovement) {
                gameObject.playerInputRight.paddleMovement = 1;
                return ;
            }
            gameObject.playerInputRight.paddleMovement++;
            if (gameObject.playerInputRight.paddleMovement > 1)
                gameObject.playerInputRight.paddleMovement = 1;
            break;
        case "8":
            // Activate the powerup
            gameObject.playerInputRight.powerupBig = true;
            break;
        case "9":
            // Activate the powerup
            gameObject.playerInputRight.powerupSpeed = true;
            break;

        default:
            return;
    }
}

export function keyReleaseCallback(event) {
    switch (event.key) {
        // Player LEFT
        case "w":
            if (!gameObject.playerInputLeft.paddleMovement) {
                gameObject.playerInputLeft.paddleMovement = 0;
                return ;
            }
            // Stop the paddle
            gameObject.playerInputLeft.paddleMovement++;
            break;
        case "s":
            if (!gameObject.playerInputLeft.paddleMovement) {
                gameObject.playerInputLeft.paddleMovement = 0;
                return ;
            }
            // Stop the paddle
            gameObject.playerInputLeft.paddleMovement--;
            break;

        // Player RIGHT
        case "o":
            if (!gameObject.playerInputRight.paddleMovement) {
                gameObject.playerInputRight.paddleMovement = 0;
                return ;
            }
            gameObject.playerInputRight.paddleMovement++;
            break;
        case "l":
            if (!gameObject.playerInputRight.paddleMovement) {
                gameObject.playerInputRight.paddleMovement = 0;
                return ;
            }
            gameObject.playerInputRight.paddleMovement--;
            break;
    }
}