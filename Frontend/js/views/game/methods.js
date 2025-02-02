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
    WebSocketManagerGame.sendMessage(message);
}

function gameLoop(currentTime) {
    if (currentTime - gameObject.lastFrameTime >= 30) {

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
	return (edgeSize / 100) * percentage;
}

export function updateGameObjects(gameState) {
    const gameField = $id("game-field");

    gameObject.state = gameState?.gameData?.state;
    gameObject.playerLeft.points = gameState.playerLeft.points;
    gameObject.playerRight.points = gameState.playerRight.points;

    gameObject.playerLeft.pos = percentageToPixels(gameState.playerLeft.paddlePos, gameField.height);
	gameObject.playerRight.pos = percentageToPixels(gameState.playerRight.paddlePos, gameField.height);
	gameObject.playerLeft.size = percentageToPixels(gameState.playerLeft.paddleSize, gameField.height);
	gameObject.playerRight.size = percentageToPixels(gameState.playerRight.paddleSize, gameField.height);
	gameObject.ball.posX = percentageToPixels(gameState.gameData.ballPosX, gameField.width);
	gameObject.ball.posY = percentageToPixels(gameState.gameData.ballPosY, gameField.height);
	gameObject.ball.size = 4;

    gameObject.playerLeft.powerups.big = gameState.playerLeft.powerupBig;
    gameObject.playerLeft.powerups.slow = gameState.playerLeft.powerupSlow;
    gameObject.playerLeft.powerups.fast = gameState.playerLeft.powerupFast;
    gameObject.playerRight.powerups.big = gameState.playerRight.powerupBig;
    gameObject.playerRight.powerups.slow = gameState.playerRight.powerupSlow;
    gameObject.playerRight.powerups.fast = gameState.playerRight.powerupFast;
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

const showGame = () => {
    const gameField = $id("game-field");
    const gameViewImageContainer = $id("game-view-image-container");
    const gameImageContainer = $id("game-view-map-image");
    const gameImage = gameImageContainer.children[0];
    gameField.style.display = "block";
    gameImage.src = window.location.origin + '/assets/game/maps/ufo.png';
    gameViewImageContainer.style.backgroundImage = "none";
    gameViewImageContainer.style.width= "100%";
    gameImage.style.display = "block";
}

const tempImageObject = {
    0: "",
    1: "https://svgsilh.com/svg/1563467.svg",
    2: "https://svgsilh.com/svg/1216173.svg",
    3: "https://svgsilh.com/svg/592740.svg",
    4: "https://svgsilh.com/svg/1563467.svg",
    5: "https://svgsilh.com/svg/1216173.svg",
    6: "https://svgsilh.com/svg/592740.svg",
}

const gameCountdownImage = (currentTime) => {
    const gameCountdownImage = $id("game-countdown-image");
    gameCountdownImage.src = tempImageObject[currentTime];
    gameCountdownImage.style.display = "block";

    if (!currentTime) {
        gameCountdownImage.style.display = "none";
    }
}

let gameCountdownIntervalId = undefined;
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
        gameCountdownIntervalId = setInterval((startTime) => {
            let diff = startTime - new Date();
            if (diff <= 0) {
                clearInterval(gameCountdownIntervalId);
                console.log("Starting game loop");
                gameCountdownImage(0);
                showGame();
                startGameLoop();
                return ;
            }

            // update image here
            console.log("gameCountdown",  startTime - new Date());
            gameCountdownImage(Math.floor(diff / 1000));
        }, 1000, Date.parse(readyStateObject.startTime));
    }
}
