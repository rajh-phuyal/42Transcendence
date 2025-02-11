import { gameObject } from "./objects.js";

export function keyPressCallback(event) {
    switch (event.key) {
        // Player LEFT
        case "w":
            // Move the paddle up
            gameObject.playerInputLeft.paddleMovement = "-";
            break;
        case "s":
            // Move the paddle down
            gameObject.playerInputLeft.paddleMovement = "+";
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
            gameObject.playerInputRight.paddleMovement = "-";
            break;
        case "l":
            gameObject.playerInputRight.paddleMovement = "+";
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
            // Stop the paddle
            gameObject.playerInputLeft.paddleMovement = "0";
            break;
        case "s":
            // Stop the paddle
            gameObject.playerInputLeft.paddleMovement = "0";
            break;

        // Player RIGHT
        case "o":
            gameObject.playerInputRight.paddleMovement = "0";
            break;
        case "l":
            gameObject.playerInputRight.paddleMovement = "0";
            break;
    }
}