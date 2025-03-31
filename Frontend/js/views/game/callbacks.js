import { gameObject } from "./objects.js";

export function keyPressCallback(event) {
    switch (event.key) {
        // Player LEFT
        case "w":
            gameObject.keyStrokes.w = true;
            break;
        case "s":
            gameObject.keyStrokes.s = true;
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
            gameObject.keyStrokes.o = true;
            break;
        case "l":
            gameObject.keyStrokes.l = true;
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
            gameObject.keyStrokes.w = false;
            break;
        case "s":
            gameObject.keyStrokes.s = false;
            break;

        // Player RIGHT
        case "o":
            gameObject.keyStrokes.o = false;
            break;
        case "l":
            gameObject.keyStrokes.l = false;
            break;
    }
}