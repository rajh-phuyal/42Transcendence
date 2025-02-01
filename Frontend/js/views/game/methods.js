import { $id, $on, $off } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';

export function changeGameState(state) {
    switch (state) {
        case "ongoing": // transition lobby to game
            $id("button-quit-game").style.display = "none";
            return ;
        case "paused": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            return ;
        case "finished": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            return ;
    }
    console.warn("FE doen't know what to do with this state:", state);
}

// function logTimeWithMilliseconds() {
//     const now = new Date();
//     const hours = now.getHours().toString().padStart(2, '0');
//     const minutes = now.getMinutes().toString().padStart(2, '0');
//     const seconds = now.getSeconds().toString().padStart(2, '0');
//     const milliseconds = now.getMilliseconds().toString().padStart(3, '0');

//     console.log(`${hours}:${minutes}:${seconds}.${milliseconds}`);
// }

async function updateServer() {
    // Send the ws message to the server
    const message = {
        messageType: "playerInput",
        paddleMovement: gameObject.playerInput.paddleMovement,
        powerupBig: gameObject.playerInput.powerupBig,
        powerupSlow: gameObject.playerInput.powerupSlow,
        powerupFast: gameObject.playerInput.powerupFast,
    }
    console.log("sending message to server:", message);
    await WebSocketManagerGame.sendMessage(message);
}

function gameLoop(currentTime) {
    console.log("gameLoop");
    if (currentTime - gameObject.lastFrameTime >= 15) {

        // Check if the game is ongoing
        // if (gameObject.state !== "ongoing") {
        //     cancelAnimationFrame(gameObject.animationId);
        //     return ;
        // }
        // Send the ws message to the server
        updateServer();
        // Render the game

        console.log("paddle movement player1:", gameObject.playerInput.paddleMovement);
        console.log("animation id:", gameObject.animationId);
        gameObject.lastFrameTime = currentTime;
    }
    gameObject.animationId = requestAnimationFrame(gameLoop);
}

function keyPressCallback(event) {
    switch (event.key) {
        case "w":
            // Move the paddle up
            gameObject.playerInput.paddleMovement = "-";
            // console.log("up");
            return ;
        case "s":
            // Move the paddle down
            gameObject.playerInput.paddleMovement = "+";
            // console.log("down");
            return ;
        case "1":
            // Activate the powerup
            gameObject.playerInput.powerupBig = true;
            // console.log("big");
            return ;
        case "2":
            // Activate the powerup
            gameObject.playerInput.powerupSlow = true;
            // console.log("slow");
            return ;
        case "3":
            // Activate the powerup
            gameObject.playerInput.powerupFast = true;
            // console.log("fast");
            return ;
    }
}

function keyReleaseCallback(event) {
    switch (event.key) {
        case "w":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            // console.log("stop");
            return ;
        case "s":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            // console.log("stop");
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
export function updateReadyState(readyStateObject) {

    if (readyStateObject.playerLeft) {
        $id("player-left-state-spinner").style.display = "none";
        $id("player-left-state").style.display = "block";
    }
    else {
        $id("player-left-state-spinner").style.display = "block";
        $id("player-left-state").style.display = "none";
    }

    if (readyStateObject.playerRight) {
        $id("player-right-state-spinner").style.display = "none";
        $id("player-right-state").style.display = "block";
    }
    else {
        $id("player-right-state-spinner").style.display = "block";
        $id("player-right-state").style.display = "none";
    }

    if (readyStateObject.startTime)
        console.warn("Start Time:", readyStateObject.startTime);
}
