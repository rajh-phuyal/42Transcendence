import { gameObject } from './objects.js';
import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import { animateImage, removeImageAnimation, showGame } from './loop.js';
import { endGameLoop } from './loop.js';
import { startGameLoop} from './loop.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { gameRender } from './render.js';
import { audioPlayer } from '../../abstracts/audio.js';

export const percentageToPixels = (side, percentage) => {
    const gameField = $id("game-field");
    if (side === "x")
        return (gameField.width - 2 * gameObject.borderStrokeWidth ) * percentage / 100;
    else if (side === "y")
        return (gameField.height - 2 * gameObject.borderStrokeWidth ) * percentage / 100;
    else
        return undefined;
}

export function changeGameState(state) {
    console.log("changeGameState", state);
    gameObject.state = state;
    switch (state) {
        case undefined:
            $id("button-play-again").style.display = "none";
            audioPlayer.play(0); // Lobby music
            showPowerupStatus(false);
            $id("button-quit-game").style.display = "none";
            break;
        case "pending":
            $id("button-play-again").style.display = "none";
            audioPlayer.play(0); // Lobby music
            showPowerupStatus(false);
            $id("button-quit-game").style.display = "block";
            if (gameObject.wsConnection)
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "connected-waiting");
            else
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "pending");
            break;
        case "countdown":
            $id("button-play-again").style.display = "none";
            audioPlayer.play(gameObject.mapId);
            audioPlayer.playSound("unpause");
            showPowerupStatus(true);
            $id("game-view-middle-side-container-top-text").innerText = "TODO: COUNTDOWN 5,4,3,2,1,0";
            break;
        case "ongoing":
            $id("button-play-again").style.display = "none";
            audioPlayer.playSound("beep2");
            $id("game-view-middle-side-container-top-text").innerText ="";
            $id("button-quit-game").style.display = "none";
            break;
        case "paused":
            $id("button-play-again").style.display = "none";
            audioPlayer.play(0); // Lobby music
            showPowerupStatus(false);
            $id("button-quit-game").style.display = "none";
            if (gameObject.wsConnection){
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "connected-waiting");
                audioPlayer.playSound("pause");
            }
            else
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "paused-connect");
            break;
        case "finished":
            $id("button-play-again").style.display = "block";
            audioPlayer.playSound("gameover");
            audioPlayer.play(0); // Lobby music
            showPowerupStatus(false);
            $id("button-quit-game").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText = "";
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "finished");
            gameObject.playerLeft.state = "finished"
            gameObject.playerRight.state = "finished"
            break;
        default:
            console.warn("FE doen't know what to do with this state:", state);
    }
    updateReadyStateNodes();
}

export function updateReadyStateNodes() {
    //console.log("Updating ready state nodes with:", gameObject.playerLeft.state, gameObject.playerRight.state);
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
            $id("player-left-state").innerText = translate("game", "ready");
            $id("player-left-state-spinner").style.display = "none";
        }
        if (gameObject.playerRight.state === "ready"){
            $id("player-right-state").innerText = translate("game", "ready");
            $id("player-right-state-spinner").style.display = "none";
        }
        // Show the score and remove the spinner
        if (gameObject.playerLeft.state === "finished"){
            $id("player-left-state").innerText = gameObject.playerLeft.points;
            $id("player-left-state-spinner").style.display = "none";
            if (gameObject.playerLeft.result === "won") {
                $id("user-card-player-left").classList.remove("user-card-looser");
                $id("user-card-player-left").classList.add("user-card-winner");
            } else {
                $id("user-card-player-left").classList.remove("user-card-winner");
                $id("user-card-player-left").classList.add("user-card-looser");
            }
        }
        if (gameObject.playerRight.state === "finished"){
            $id("player-right-state").innerText = gameObject.playerRight.points;
            $id("player-right-state-spinner").style.display = "none";
            if (gameObject.playerRight.result === "won") {
                $id("user-card-player-right").classList.remove("user-card-looser");
                $id("user-card-player-right").classList.add("user-card-winner");
            } else {
                $id("user-card-player-right").classList.remove("user-card-winner");
                $id("user-card-player-right").classList.add("user-card-looser");
            }
        }
}

// available / using / used / unavailable
function setPowerupImg(element, powerupName, state) {
    let filename = `${window.origin}/assets/game/icons/powerup-` + state + `-` + powerupName + `.png`;
        element.src = filename;
}

export function showPowerupStatus(visible) {
    let elements = $class('player-powerup-status')
    for (let element of elements)
        element.style.display = visible ? element.style.display = "flex" : element.style.display = "none";
    if (!visible)
        return;
    setPowerupImg($id('player-left-powerups-big'), 'big',  gameObject.playerLeft.powerupBig);
    setPowerupImg($id('player-left-powerups-slow'), 'slow',  gameObject.playerLeft.powerupSlow);
    setPowerupImg($id('player-left-powerups-fast'), 'fast',  gameObject.playerLeft.powerupFast);
    setPowerupImg($id('player-right-powerups-big'), 'big',  gameObject.playerRight.powerupBig);
    setPowerupImg($id('player-right-powerups-slow'), 'slow',  gameObject.playerRight.powerupSlow);
    setPowerupImg($id('player-right-powerups-fast'), 'fast',  gameObject.playerRight.powerupFast);
}

export function updateReadyStatefromWS(readyStateObject) {
    let gameCountdownIntervalId = undefined;

    // Remove paused banner:
    $id("game-view-middle-side-container-top-text").innerText = "";

    // To stop a potential ongoing game we need to:
    endGameLoop();

    gameObject.playerLeft.state = readyStateObject.playerLeft ? "ready" : "waiting";
    gameObject.playerRight.state = readyStateObject.playerRight ? "ready" : "waiting";
    //console.log("updateReadyState", gameObject.playerLeft.state, gameObject.playerRight.state);
    updateReadyStateNodes();

    if (readyStateObject.startTime) {
        animateImage("game-countdown-image", "pulsate", "1s", "infinite");
        changeGameState("countdown");
        startGameLoop();
        gameCountdownIntervalId = setInterval((startTime) => {
            let diff = Math.floor((startTime - new Date()) / 1000);
            if (diff <= 0) {
                clearInterval(gameCountdownIntervalId);
                gameCountdownImage(0);
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

export function updateGameObjects(beMessage) {
    // The first time we get the state ongoing we need to set it
    if ( beMessage?.gameData?.state === "ongoing" && gameObject.state !== "ongoing")
        changeGameState("ongoing");
    gameObject.state = beMessage?.gameData?.state;
    gameObject.sound = beMessage?.gameData?.sound;
    gameObject.playerLeft.points = beMessage?.playerLeft?.points;
    gameObject.playerLeft.size = percentageToPixels('y', beMessage?.playerLeft?.paddleSize);
    gameObject.playerLeft.pos = percentageToPixels('y', beMessage?.playerLeft?.paddlePos) - gameObject.playerLeft.size / 2; // Center the paddle
    gameObject.playerLeft.powerupBig = beMessage?.playerLeft?.powerupBig;
    gameObject.playerLeft.powerupSlow = beMessage?.playerLeft?.powerupSlow;
    gameObject.playerLeft.powerupFast = beMessage?.playerLeft?.powerupFast;
    gameObject.playerRight.points = beMessage?.playerRight?.points;
    gameObject.playerRight.size = percentageToPixels('y', beMessage?.playerRight?.paddleSize);
    gameObject.playerRight.pos = percentageToPixels('y', beMessage?.playerRight?.paddlePos) - gameObject.playerRight.size / 2; // Center the paddle
    gameObject.playerRight.powerupBig = beMessage?.playerRight?.powerupBig;
    gameObject.playerRight.powerupSlow = beMessage?.playerRight?.powerupSlow;
    gameObject.playerRight.powerupFast = beMessage?.playerRight?.powerupFast;
    gameObject.ball.posX = percentageToPixels('x', beMessage?.ball?.posX);
    gameObject.ball.posY = percentageToPixels('y', beMessage?.ball?.posY);
    gameObject.ball.height = percentageToPixels('y', beMessage?.ball?.height);
    gameObject.ball.width = percentageToPixels('x', beMessage?.ball?.width);
    // If the state is not ongoing we should render manually!
    // So when establishing a connection we can render the game state
    if (gameObject.state != "ongoing" && gameObject.state != "countdown") {
        changeGameState(gameObject.state);
        gameRender();
    }
}

export function sendPlayerInput() {
    //Send the ws message to the server
    const message = {
        messageType: "playerInput",
        playerLeft: {
            movePaddle: gameObject.playerInputLeft.paddleMovement || "0",
            activatePowerupBig: gameObject.playerInputLeft.powerupBig || false,
            activatePowerupSpeed: gameObject.playerInputLeft.powerupSpeed || false
        },
        playerRight: {
            movePaddle: gameObject.playerInputRight.paddleMovement || "0",
            activatePowerupBig: gameObject.playerInputRight.powerupBig || false,
            activatePowerupSpeed: gameObject.playerInputRight.powerupSpeed || false
        }
    }
    WebSocketManagerGame.sendMessage(message);
    // Reset powerup states
    gameObject.playerInputLeft.powerupBig = false;
    gameObject.playerInputLeft.powerupSpeed = false;
    gameObject.playerInputRight.powerupBig = false;
    gameObject.playerInputRight.powerupSpeed = false;
}
















// TODO: do we need the stuff below? #304
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

// TODO: do we need the stuff below? #304
const gameCountdownImage = (currentTime) => {
    const gameCountdownImage = $id("game-countdown-image");
    gameCountdownImage.src = countdownImageObject[currentTime];
    gameCountdownImage.style.display = "block";

    if (!currentTime) {
        gameCountdownImage.style.display = "none";
    }
}