import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import { keyPressCallback, keyReleaseCallback } from './callbacks.js';
import { showPowerupStatus, sendPlayerInput, changeGameState } from './methods.js';
import { gameRender } from './render.js';

function gameLoop(currentTime) {
    if (currentTime - gameObject.lastFrameTime >= gameObject.frameTime) {
        gameObject.lastFrameTime = currentTime;
        if (gameObject.state === "ongoing")
            sendPlayerInput();
            showPowerupStatus(true);
        gameRender();
        // Check if the game is  still ongoing
        if (gameObject.state != "ongoing" && gameObject.state != "countdown") {
            console.log("Game is not ongoing/coutdown anymore: ending game loop");
            cancelAnimationFrame(gameObject.animationId);
            return;
        }
    }
    gameObject.animationId = requestAnimationFrame(gameLoop);
}

export function startGameLoop() {
    //Just in case we have an ongoing game loop end it
    endGameLoop();
    //console.log("Starting game loop");
    $on(document, 'keydown', keyPressCallback);
    $on(document, 'keyup', keyReleaseCallback);
    gameObject.lastFrameTime = performance.now();
    gameObject.animationId = requestAnimationFrame(gameLoop);
    showPowerupStatus(true);
}

export function endGameLoop() {
    //console.log("Ending game loop");
    cancelAnimationFrame(gameObject.animationId);
    $off(document, 'keydown', keyPressCallback);
    $off(document, 'keyup', keyReleaseCallback);
    gameRender(); // One last render to show the final state
}

export const animateImage = (
    id,
    animationName,
    duration = "1s",
    iterationCount = "1",
    timingFunction = "ease-in-out"
) => {
    const image = $id(id);
    //image.style.animationDuration = duration;
    //image.style.animationName = animationName;
    //image.style.animationIterationCount = iterationCount;
    //image.style.animationTimingFunction = timingFunction;
};

export const removeImageAnimation = (id) => {
    const image = $id(id);
    //image.style.animationDuration = "0s";
    //image.style.animationName = "";
    //image.style.animationIterationCount = "0";
}

export const showGame = () => {
    const gameField = $id("game-field");
    const gameViewImageContainer = $id("game-view-image-container");
    const gameImageContainer = $id("game-view-map-image");

    const gameImage = gameImageContainer.children[0];

    gameViewImageContainer.style.backgroundImage = "none";
    gameViewImageContainer.style.width = "100%";
    gameField.style.display = "block";

    gameImage.style.display = "block";
    animateImage("game-view-map-image", "fadein", "3s");
}
