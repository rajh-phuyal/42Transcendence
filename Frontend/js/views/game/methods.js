import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { gameRender } from './render.js';
import AudioPlayer from '../../abstracts/audio.js';
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export function changeGameState(state) {
    gameObject.state = state;

   /*  // For debug TODO: remove
    $id("game-view-left-side-container-bottom").innerText = "GAME STATE: " + state;

    switch (state) {
        case undefined:
            updateReadyStateNodes();
            showPowerupStatus(false);
            return;
        case "ongoing": // transition lobby to game
            $id("button-quit-game").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText ="";
            return;
        case "paused": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "paused");
            return;
        case "pending":
            $id("button-quit-game").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "pending7");
            return;
        case "finished": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            $id("player-left-state-spinner").style.display = "none";
            $id("player-right-state-spinner").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText = "";
            return;
    }
    console.warn("FE doen't know what to do with this state:", state); */
}

function sendPlayerInput() {
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
        sendPlayerInput();
        updatePowerupStatus();
        gameRender();
        gameObject.lastFrameTime = currentTime;
        // Check if the game is  still ongoing
        if (gameObject.state !== "ongoing") {
            console.log("Game is not ongoing anymore: ending game loop");
            cancelAnimationFrame(gameObject.animationId);
            return;
        }
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
}

const percentageToPixels = (percentage, edgeSize) => {
    return (edgeSize / 100) * percentage;
}

export function updateGameObjects(beMessage) {
    const gameField = $id("game-field");

    gameObject.state = beMessage?.gameData?.state;
    gameObject.sound = beMessage?.gameData?.sound;
    gameObject.playerLeft.points = beMessage?.playerLeft?.points;
    gameObject.playerLeft.pos = percentageToPixels(beMessage?.playerLeft?.paddlePos, gameField?.height);
    gameObject.playerLeft.size = percentageToPixels(beMessage?.playerLeft?.paddleSize, gameField?.height);
    gameObject.playerLeft.powerupBig = beMessage?.playerLeft?.powerupBig;
    gameObject.playerLeft.powerupSlow = beMessage?.playerLeft?.powerupSlow;
    gameObject.playerLeft.powerupFast = beMessage?.playerLeft?.powerupFast;
    gameObject.playerRight.points = beMessage?.playerRight?.points;
    gameObject.playerRight.pos = percentageToPixels(beMessage?.playerRight?.paddlePos, gameField?.height);
    gameObject.playerRight.size = percentageToPixels(beMessage?.playerRight?.paddleSize, gameField?.height);
    gameObject.playerRight.powerupBig = beMessage?.playerRight?.powerupBig;
    gameObject.playerRight.powerupSlow = beMessage?.playerRight?.powerupSlow;
    gameObject.playerRight.powerupFast = beMessage?.playerRight?.powerupFast;
    gameObject.ball.posX = percentageToPixels(beMessage?.ball?.posX, gameField?.width);
    gameObject.ball.posY = percentageToPixels(beMessage?.ball?.posY, gameField?.height);
    gameObject.ball.height = percentageToPixels(beMessage?.ball?.height, gameField?.height);
    gameObject.ball.width = percentageToPixels(beMessage?.ball?.width, gameField?.height);
    // If the state is not ongoing we should render manually!
    // So when establishing a connection we can render the game state
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

export function updateReadyStateNodes() {
    // Hide the ready message and the spinner (for finished, ongoing games)
    if (gameObject.playerLeft.state === undefined){
        $id("player-left-state").innerHTML = "";
        $id("player-left-state-spinner").style.display = "none";
    }
    if (gameObject.playerRight.state === undefined){
        $id("player-right-state").innerHTML = "";
        $id("player-right-state-spinner").style.display = "none";
    }
    // Show the spinner and remove the text
    if (gameObject.playerLeft.state === "waiting"){
        $id("player-left-state").innerHTML = "";
        $id("player-left-state-spinner").style.display = "block";
    }
    if (gameObject.playerRight.state === "waiting"){
        $id("player-right-state").innerHTML = "";
        $id("player-right-state-spinner").style.display = "block";
    }
    // Show the message and remove the spinner
    if (gameObject.playerLeft.state === "ready"){
        $id("player-left-state").innerHTML = translate("game", "ready");
        $id("player-left-state-spinner").style.display = "none";
    }
    if (gameObject.playerRight.state === "ready"){
        $id("player-right-state").innerHTML = translate("game", "ready");
        $id("player-right-state-spinner").style.display = "none";
    }
}

export function showPowerupStatus(value) {
        let elements = $class('player-powerup-status')
        for (let element of elements)
            element.style.display = value ? element.style.display = "flex" : element.style.display = "none";

        colorPowerupStatus($id('player-left-powerups-big'), gameObject.playerLeft.powerupBig);
        colorPowerupStatus($id('player-left-powerups-slow'), gameObject.playerLeft.powerupSlow);
        colorPowerupStatus($id('player-left-powerups-fast'), gameObject.playerLeft.powerupFast);
        colorPowerupStatus($id('player-right-powerups-big'), gameObject.playerRight.powerupBig);
        colorPowerupStatus($id('player-right-powerups-slow'), gameObject.playerRight.powerupSlow);
        colorPowerupStatus($id('player-right-powerups-fast'), gameObject.playerRight.powerupFast);
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

export function endGameLoop() {
    console.log("Ending game loop");
    cancelAnimationFrame(gameObject.animationId);
    $off(document, 'keydown', keyPressCallback);
    $off(document, 'keyup', keyReleaseCallback);
    showPowerupStatus(false); // TO show the spinners again
    gameRender(); // One last render to show the final state
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
