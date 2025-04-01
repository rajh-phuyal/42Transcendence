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
        case "a":
            // Activate the powerup
            gameObject.playerInputLeft.powerupBig = true;
            break;
        case "d":
            // Activate the powerup
            gameObject.playerInputLeft.powerupSpeed = true;
            break;

        // Player RIGHT
        case "ArrowUp":
            gameObject.keyStrokes.o = true;
            break;
        case "ArrowDown":
            gameObject.keyStrokes.l = true;
            break;
        case "ArrowRight":
            // Activate the powerup
            gameObject.playerInputRight.powerupBig = true;
            break;
        case "ArrowLeft":
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
        case "ArrowUp":
            gameObject.keyStrokes.o = false;
            break;
        case "ArrowDown":
            gameObject.keyStrokes.l = false;
            break;
    }
}