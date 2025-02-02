import { $id, $on, $off } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { gameRender } from './render.js';

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

function updatePlayerInput() {
    // Send the ws message to the server
    const message = {
        messageType: "playerInput",
        movePaddle: gameObject.playerInput.paddleMovement || "0",
        powerupBig: gameObject.playerInput.powerupBig || false,
        powerupSlow: gameObject.playerInput.powerupSlow || false,
        powerupFast: gameObject.playerInput.powerupFast || false,
    }
    console.log("sending message to server:", message);
    WebSocketManagerGame.sendMessage(message);
}

function gameLoop(currentTime) {
    console.log("gameLoop");
    if (currentTime - gameObject.lastFrameTime >= 100) {

        // Check if the game is ongoing
        if (gameObject.state !== "ongoing") {
            cancelAnimationFrame(gameObject.animationId);
            return ;
        }
        // Render the game
        // console.log("player1:", gameObject.playerLeft.pos);
        // console.log("player2:", gameObject.playerRight.pos);
        updatePlayerInput();
        gameRender();

        gameObject.lastFrameTime = currentTime;
    }
    gameObject.animationId = requestAnimationFrame(gameLoop);
}

function keyPressCallback(event) {
    console.log("keyPressCallback", event.key);
    switch (event.key) {
        case "w":
            // Move the paddle up
            gameObject.playerInput.paddleMovement = "-";
            break;
        case "s":
            // Move the paddle down
            gameObject.playerInput.paddleMovement = "+";
            break;
        case "1":
            // Activate the powerup
            gameObject.playerInput.powerupBig = true;
            break;
        case "2":
            // Activate the powerup
            gameObject.playerInput.powerupSlow = true;
            break;
        case "3":
            // Activate the powerup
            gameObject.playerInput.powerupFast = true;
            break;
        default:
            return;
    }
}

function keyReleaseCallback(event) {
    switch (event.key) {
        case "w":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            break;
        case "s":
            // Stop the paddle
            gameObject.playerInput.paddleMovement = "0";
            break;
    }
}

const percentageToPixels = (percentage, edgeSize) => {
	console.log("percentageToPixels", percentage, edgeSize);
	return (edgeSize / 100) * percentage;
}

const normalizeGameObject = (gameObject, gameField) => {
	const normalizedGameObject = { ...gameObject };
	normalizedGameObject.playerLeft.pos = percentageToPixels(gameObject.playerLeft.pos, gameField.height);
	normalizedGameObject.playerRight.pos = percentageToPixels(gameObject.playerRight.pos, gameField.height);
	normalizedGameObject.playerLeft.size = percentageToPixels(gameObject.playerLeft.size, gameField.height);
	normalizedGameObject.playerRight.size = percentageToPixels(gameObject.playerRight.size, gameField.height);
	normalizedGameObject.ball.posX = percentageToPixels(gameObject.ball.posX, gameField.width);
	normalizedGameObject.ball.posY = percentageToPixels(gameObject.ball.posY, gameField.height);
	normalizedGameObject.ball.size = 4;
	console.log("normalizedGameObject", normalizedGameObject);
	return normalizedGameObject;
}

export function updateGameObjects(gameState) {
    const gameField = $id("game-field");

    gameObject.state = gameState?.gameData?.state;
    gameObject.playerLeft.points = gameState.playerLeft.points;
    gameObject.playerRight.points = gameState.playerRight.points;
    gameObject.playerLeft.pos = gameState.playerLeft.paddlePos;
    gameObject.playerRight.pos = gameState.playerRight.paddlePos;
    gameObject.playerLeft.size = gameState.playerLeft.paddleSize;
    gameObject.playerRight.size = gameState.playerRight.paddleSize;
    gameObject.ball.posX = gameState.gameData.ballPosX;
    gameObject.ball.posY = gameState.gameData.ballPosY;
    gameObject.playerLeft.powerups.big = gameState.playerLeft.powerupBig;
    gameObject.playerLeft.powerups.slow = gameState.playerLeft.powerupSlow;
    gameObject.playerLeft.powerups.fast = gameState.playerLeft.powerupFast;
    gameObject.playerRight.powerups.big = gameState.playerRight.powerupBig;
    gameObject.playerRight.powerups.slow = gameState.playerRight.powerupSlow;
    gameObject.playerRight.powerups.fast = gameState.playerRight.powerupFast;

    const normalizedGameObject = normalizeGameObject(gameObject, gameField);

    gameObject = {
        ...gameObject,
        ...normalizedGameObject,
    }
}

export function endGameLoop() {
    cancelAnimationFrame(gameObject.animationId);
    $off(document, 'keydown', keyPressCallback);
    $off(document, 'keyup', keyReleaseCallback);
}

export function startGameLoop() {
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

    if (readyStateObject.startTime) {
        console.warn("Start Time:", readyStateObject.startTime);
        setTimeout(() => {
            console.log("Starting game loop");
            startGameLoop();
        }, Date.parse(readyStateObject.startTime) - Date.now());
    }
}
