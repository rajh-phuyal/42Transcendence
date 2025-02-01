import { $id, $on, $off } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';

export function changeGameState(state) {
    switch (state) {
        case "pending":
            $id("button-quit-game").style.display = "flex";
            return ;
        case "ongoing":
            $id("button-quit-game").style.display = "none";
            return ;
        case "paused":
            $id("button-quit-game").style.display = "none";
            return ;
        case "finished":
            $id("button-quit-game").style.display = "none";
            return ;
    }
    console.warn("FE doen't know what to do with this state:", state);
}

function logTimeWithMilliseconds() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    const milliseconds = now.getMilliseconds().toString().padStart(3, '0');

    console.log(`${hours}:${minutes}:${seconds}.${milliseconds}`);
}



function gameLoop(currentTime) {
    if (currentTime - gameObject.lastFrameTime >= 15) {

        // Check if the game is ongoing
        if (gameObject.state !== "ongoing") {
            cancelAnimationFrame(animationId);
            return ;
        }
        // Check if there's any key input to move the paddle/powerups

        // Send the ws message to the server
        // Render the game

        console.log(logTimeWithMilliseconds());

        gameObject.lastFrameTime = currentTime;
    }
    requestAnimationFrame(gameLoop);
}

function keyPressCallback(event) {
    switch (event.key) {
        case "w":
            // Move the paddle up
            gameObject.playerInput.paddleMovement = "-";
            return ;
        case "s":
            // Move the paddle down
            gameObject.playerInput.paddleMovement = "+";
            return ;
        case "1":
            // Activate the powerup
            gameObject.playerInput.powerupBig = true;
        case "2":
            // Activate the powerup
            gameObject.playerInput.powerupSlow = true;
        case "3":
            // Activate the powerup
            gameObject.playerInput.powerupFast = true;
            return ;
    }
}

function keyReleaseCallback(event) {
    switch (event.key) {
        case "w":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            return ;
        case "s":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            return ;
    }
}

export function updateGameObjects(gameState) {
    gameObject.state = gameState.state;
    gameObject.playerLeft.points = gameState.playerLeft.points;
    gameObject.playerRight.points = gameState.playerRight.points;
    gameObject.playerLeft.pos = gameState.playerLeft.paddlePos;
    gameObject.playerRight.pos = gameState.playerRight.paddlePos;
    gameObject.playerLeft.size = gameState.playerLeft.paddleSize;
    gameObject.playerRight.size = gameState.playerRight.paddleSize;
    gameObject.ball.posX = gameState.ball.ballPosX;
    gameObject.ball.posY = gameState.ball.ballPosY;
    gameObject.playerLeft.powerups.big = gameState.playerLeft.powerupsBig;
    gameObject.playerLeft.powerups.slow = gameState.playerLeft.powerupsSlow;
    gameObject.playerLeft.powerups.fast = gameState.playerLeft.powerupsFast;
    gameObject.playerRight.powerups.big = gameState.playerRight.powerupsBig;
    gameObject.playerRight.powerups.slow = gameState.playerRight.powerupsSlow;
    gameObject.playerRight.powerups.fast = gameState.playerRight.powerupsFast;
}

export function endGameLoop() {
    cancelAnimationFrame(gameObject.animationId);
    $off(document, 'keydown', keyPressCallback);
    $off(document, 'keyup', keyReleaseCallback);
}

export function startGameLoop() {
    //TODO: Time it with the start game timestamp
    $on(document, 'keydown', keyPressCallback);
    $on(document, 'keyup', keyReleaseCallback);
    gameObject.lastFrameTime = performance.now();
    gameObject.animationId = requestAnimationFrame(gameLoop);
}
