import { gameObject } from './objects.js';
import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import { animateImage, removeImageAnimation, showGame } from './loop.js';
import { endGameLoop } from './loop.js';
import { startGameLoop} from './loop.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { gameRender } from './render.js';

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
            showPowerupStatus(false);
            break;
        case "pending":
            showPowerupStatus(false);
            $id("button-quit-game").style.display = "none";
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "pending");
            break;
        case "countdown":
            showPowerupStatus(true);
            $id("game-view-middle-side-container-top-text").innerText = "TODO: COUNTDOWN 5,4,3,2,1,0";
            break;
        case "ongoing":
            $id("game-view-middle-side-container-top-text").innerText ="";
            $id("button-quit-game").style.display = "none";
            break;
        case "paused":
            showPowerupStatus(false);
            if (gameObject.playMusic)
                //TODO: audioPlayer.play(0); // Lobby music
            $id("button-quit-game").style.display = "none";
            if (gameObject.wsConnection){
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "paused-waiting");
                if(gameObject.playSounds)
                    audioPlayer.playSound("pause");
            }
            else
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "paused-connect");
            break;
        case "finished":
            if (gameObject.playMusic)
                //TODO: audioPlayer.play(0); // Lobby music
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
    console.log("Updating ready state nodes with:", gameObject.playerLeft.state, gameObject.playerRight.state);
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
        }
        if (gameObject.playerRight.state === "finished"){
            $id("player-right-state").innerText = gameObject.playerRight.points;
            $id("player-right-state-spinner").style.display = "none";
        }
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

export function showPowerupStatus(visible) {
    console.log("Showing powerup status");
    let elements = $class('player-powerup-status')
    for (let element of elements)
        element.style.display = visible ? element.style.display = "flex" : element.style.display = "none";
    colorPowerupStatus($id('player-left-powerups-big'), gameObject.playerLeft.powerupBig);
    colorPowerupStatus($id('player-left-powerups-slow'), gameObject.playerLeft.powerupSlow);
    colorPowerupStatus($id('player-left-powerups-fast'), gameObject.playerLeft.powerupFast);
    colorPowerupStatus($id('player-right-powerups-big'), gameObject.playerRight.powerupBig);
    colorPowerupStatus($id('player-right-powerups-slow'), gameObject.playerRight.powerupSlow);
    colorPowerupStatus($id('player-right-powerups-fast'), gameObject.playerRight.powerupFast);
}

export function updateReadyState(readyStateObject) {
    let gameCountdownIntervalId = undefined;

    // Remove paused banner:
    $id("game-view-middle-side-container-top-text").innerText = "";

    // To stop a potential ongoing game we need to:
    endGameLoop();

    gameObject.playerLeft.state = readyStateObject.playerLeft ? "ready" : "waiting";
    gameObject.playerRight.state = readyStateObject.playerRight ? "ready" : "waiting";
    console.log("updateReadyState", gameObject.playerLeft.state, gameObject.playerRight.state);
    updateReadyStateNodes();

    if (readyStateObject.startTime) {
        // Change music
        if (gameObject.playMusic)
            //TODO: audioPlayer.play(gameObject.mapId);
        if (gameObject.state === "paused" || gameObject.playSounds)
            audioPlayer.playSound("unpause");
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
    console.log("Updating game objects");
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
    if (gameObject.state !== "ongoing")
        console.log("Rendering game state manually");
        changeGameState(gameObject.state);
        gameRender();
}

// TODO: move to audio player file
export function toggleMusic(value=undefined) {
    // If not defined toggle the music, else set the value
    if (value === undefined)
        gameObject.playMusic = !gameObject.playMusic;
    else
        gameObject.playMusic = value;
    if (gameObject.playSounds)
        audioPlayer.playSound("toggle");
    if(gameObject.playMusic)
        $id("game-music-icon").src = window.origin + '/assets/game/icons/sound-on.png';
    else
        $id("game-music-icon").src = window.origin + '/assets/game/icons/sound-off.png';

    console.log("playMusic", gameObject.mapId);
    if (gameObject.playMusic && gameObject.state === "ongoing")
        //TODO: audioPlayer.play(gameObject.mapId);
    else if (gameObject.playMusic && gameObject.state !== "ongoing")
        //TODO: audioPlayer.play(0); // Lobby music
    else
        audioPlayer.stop();
}

// TODO: move to audio player file
export function toggleSound(value=undefined) {
    // If not defined toggle the sounds, else set the value
    if (value === undefined)
        gameObject.playSounds = !gameObject.playSounds;
    else
        gameObject.playSounds = value;
    if (gameObject.playSounds)
        audioPlayer.playSound("toggle");
    if(gameObject.playSounds)
        $id("game-sound-icon").src = window.origin + '/assets/game/icons/music-on.png';
    else
        $id("game-sound-icon").src = window.origin + '/assets/game/icons/music-off.png';
}

export function sendPlayerInput() {
    console.log("Sending player input");
    //Send the ws message to the server
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