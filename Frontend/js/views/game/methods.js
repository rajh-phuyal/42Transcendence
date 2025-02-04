import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { gameRender } from './render.js';
import router from '../../navigation/router.js';

export function changeGameState(state) {
    // For debug TODO: remove
    $id("game-view-left-side-container-bottom").innerText = "GAME STATE: " + state;
    switch (state) {
        case "ongoing": // transition lobby to game
            $id("button-quit-game").style.display = "none";
            return;
        case "paused": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            return;
        case "finished": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            $id("player-left-state-spinner").style.display = "none";
            $id("player-right-state-spinner").style.display = "none";
            return;
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
        playerLeft: {
            movePaddle: gameObject.playerInputLeft.paddleMovement || "0",
            activatePowerupBig: gameObject.playerInputLeft.powerupBig || false,
            activatePowerupSlow: gameObject.playerInputLeft.powerupSlow || false,
            activatePowerupFast: gameObject.playerInputLeft.powerupFast || false
        },
        playerRight: {
            movePaddle: gameObject.playerInputRight.paddleMovement || "0",
            activatePowerupBig: gameObject.playerInputRight.powerupBig || false,
            activatePowerupSlow: gameObject.playerInputRight.powerupSlow || false,
            activatePowerupFast: gameObject.playerInputRight.powerupFast || false
        }
    }
    WebSocketManagerGame.sendMessage(message);
}

function gameLoop(currentTime) {
    if (currentTime - gameObject.lastFrameTime >= gameObject.frameTime) {
        updatePlayerInput();
        updatePowerupStatus();
        gameRender();
        // Check if the game is ongoing
        if (gameObject.state !== "ongoing") {
            console.log("Game is not ongoing anymore: ending game loop");
            cancelAnimationFrame(gameObject.animationId);
            return;
        }
        gameObject.lastFrameTime = currentTime;
    }
    gameObject.animationId = requestAnimationFrame(gameLoop);
}

function keyPressCallback(event) {
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
            gameObject.playerInputLeft.powerupSlow = true;
            break;
        case "3":
            // Activate the powerup
            gameObject.playerInputLeft.powerupFast = true;
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
            gameObject.playerInputRight.powerupSlow = true;
            break;
        case "0":
            // Activate the powerup
            gameObject.playerInputRight.powerupFast = true;
            break;

        default:
            return;
    }
    updatePlayerInput();
}

function keyReleaseCallback(event) {
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
    updatePlayerInput();
}

const percentageToPixels = (percentage, edgeSize) => {
    return (edgeSize / 100) * percentage;
}

export function updateGameObjects(gameState) {
    const gameField = $id("game-field");

    gameObject.state = gameState?.gameData?.state;
    gameObject.playerLeft.points = gameState?.playerLeft?.points;
    gameObject.playerRight.points = gameState?.playerRight?.points;

    // TODO: remove only for debugging:
    $id("game-view-left-side-container-bottom").innerHTML = "GAME STATE: " + gameObject.state + "<br>(" + gameObject.playerLeft.points +":" + gameObject.playerRight.points + ")";

    gameObject.playerLeft.pos = percentageToPixels(gameState?.playerLeft?.paddlePos, gameField?.height);
    gameObject.playerRight.pos = percentageToPixels(gameState?.playerRight?.paddlePos, gameField?.height);
    gameObject.playerLeft.size = percentageToPixels(gameState?.playerLeft?.paddleSize, gameField?.height);
    gameObject.playerRight.size = percentageToPixels(gameState?.playerRight?.paddleSize, gameField?.height);
    gameObject.ball.posX = percentageToPixels(gameState?.gameData?.ballPosX, gameField?.width);
    gameObject.ball.posY = percentageToPixels(gameState?.gameData?.ballPosY, gameField?.height);
    gameObject.ball.size = 4;

    gameObject.playerLeft.powerups.big = gameState?.playerLeft?.powerupBig;
    gameObject.playerLeft.powerups.slow = gameState?.playerLeft?.powerupSlow;
    gameObject.playerLeft.powerups.fast = gameState?.playerLeft?.powerupFast;
    gameObject.playerRight.powerups.big = gameState?.playerRight?.powerupBig;
    gameObject.playerRight.powerups.slow = gameState?.playerRight?.powerupSlow;
    gameObject.playerRight.powerups.fast = gameState?.playerRight?.powerupFast;

    // If the state is not ongoing we should render manually!
    // So when establishing a connection we can render the game state
    console.log("GAME STATE: ", gameObject.state);
    if (gameObject.state !== "ongoing")
        console.log("Rendering game state manually");
        gameRender();
}

// available / using / used / unavailable
// TODO: @xico I guess we have to choose prettier colors later on :D
function colorPowerupStatus(element, state) {
    if (state == "available")
        element.style.color = "green";
    else if (state == "using")
        element.style.color = "orange";
    else if (state == "used")
        element.style.color = "red";
    else
        element.style.color = "gray";
}

function updatePowerupStatus() {
    colorPowerupStatus($id('player-left-powerups-big'), gameObject.playerLeft.powerups.big);
    colorPowerupStatus($id('player-left-powerups-fast'), gameObject.playerLeft.powerups.fast);
    colorPowerupStatus($id('player-left-powerups-slow'), gameObject.playerLeft.powerups.slow);
    colorPowerupStatus($id('player-right-powerups-big'), gameObject.playerRight.powerups.big);
    colorPowerupStatus($id('player-right-powerups-fast'), gameObject.playerRight.powerups.fast);
    colorPowerupStatus($id('player-right-powerups-slow'), gameObject.playerRight.powerups.slow);
}

export function showPowerupStatus(value) {
        let elements = $class('user-state')
        for (let element of elements)
            value ? element.style.display = "none" : element.style.display = "flex";

        $id("player-left-state-spinner").style.display = value ? "none" : "block";
        $id("player-right-state-spinner").style.display = value ? "none" : "block";

        elements = $class('player-powerup-status')

        for (let element of elements)
            element.style.display = value ? element.style.display = "flex" : element.style.display = "none";

        updatePowerupStatus();
}

export function endGameLoop() {
    console.log("Ending game loop");
    cancelAnimationFrame(gameObject.animationId);
    $off(document, 'keydown', keyPressCallback);
    $off(document, 'keyup', keyReleaseCallback);
    showPowerupStatus(false); // TO show the spinners again
    gameRender(); // One last render to show the final state
}

export function startGameLoop() {
    //Just in case we have an ongoing game loop end it
    endGameLoop();
    console.log("Starting game loop");
    $on(document, 'keydown', keyPressCallback);
    $on(document, 'keyup', keyReleaseCallback);
    gameObject.lastFrameTime = performance.now();

    // THIS DOESNT WORK:
    // Because of a small time offset we need to wait for the state to be updated
    // If not the loop would start and immediately end
    // while (gameObject.state !== "ongoing") {
    //     console.log("Waiting for game state to be ongoing. current state: ", gameObject.state);
    //     setTimeout(() => { }, 1000);
    // }
    gameObject.animationId = requestAnimationFrame(gameLoop);
    showPowerupStatus(true);
}

const animateImage = (
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

const removeImageAnimation = (id) => {
    const image = $id(id);
    //image.style.animationDuration = "0s";
    //image.style.animationName = "";
    //image.style.animationIterationCount = "0";
}


const showGame = () => {
    const gameField = $id("game-field");
    const gameViewImageContainer = $id("game-view-image-container");
    const gameImageContainer = $id("game-view-map-image");

    const gameImage = gameImageContainer.children[0];

    // TODO: add proper map image
    gameImage.src = window.location.origin + '/assets/game/maps/ufo.png';

    gameViewImageContainer.style.backgroundImage = "none";
    gameViewImageContainer.style.width = "100%";
    gameField.style.display = "block";

    gameImage.style.display = "block";
    animateImage("game-view-map-image", "fadein", "3s");
}

const countdownImageObject = {
    0: "",
    1: `${window.origin}/assets/game/countdown/countdown1.png`,
    2: `${window.origin}/assets/game/countdown/countdown2.png`,
    3: `${window.origin}/assets/game/countdown/countdown3.png`,
    4: `${window.origin}/assets/game/countdown/countdown4.png`,
    5: `${window.origin}/assets/game/countdown/countdown5.png`,
    6: `${window.origin}/assets/game/countdown/countdown6.png`,
    7: `${window.origin}/assets/game/countdown/countdown7.png`,
    8: `${window.origin}/assets/game/countdown/countdown8.png`,
    9: `${window.origin}/assets/game/countdown/countdown9.png`,
}

const gameCountdownImage = (currentTime) => {
    const gameCountdownImage = $id("game-countdown-image");
    gameCountdownImage.src = countdownImageObject[currentTime];
    gameCountdownImage.style.display = "block";

    if (!currentTime) {
        gameCountdownImage.style.display = "none";
    }
}

let gameCountdownIntervalId = undefined;
export function updateReadyState(readyStateObject) {

    // To stop a potential ongoing game we need to:
    //endGameLoop();

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
        animateImage("game-countdown-image", "pulsate", "1s", "infinite");
        gameCountdownIntervalId = setInterval((startTime) => {
            let diff = Math.floor((startTime - new Date()) / 1000);
            if (diff <= 0) {
                clearInterval(gameCountdownIntervalId);
                gameCountdownImage(0);
                startGameLoop();
                return;
            }

            if (diff == 3) {
                console.log("Fading in map image");
                showGame();
                setTimeout(() => {
                    removeImageAnimation("game-view-map-image");
                }, 3000);
            }

            // update image here
            gameCountdownImage(diff);
        }, 1000, Date.parse(readyStateObject.startTime));
    }
}
