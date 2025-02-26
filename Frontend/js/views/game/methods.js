import { gameObject } from './objects.js';
import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import { animateImage, removeImageAnimation, showGame } from './loop.js';
import { endGameLoop } from './loop.js';
import { startGameLoop} from './loop.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { audioPlayer } from '../../abstracts/audio.js';
import { toggleGamefieldVisible, gameRender } from './render.js';

export const percentageToPixels = (side, percentage) => {
    const gameField = $id("game-field");
    if (side === "x")
        return ((gameField.width - 2 * gameObject.borderStrokeWidth ) * percentage / 100);
    else if (side === "y")
        return ((gameField.height - 2 * gameObject.borderStrokeWidth ) * percentage / 100);
    else
        return undefined;
}

export function changeGameState(state) {
    console.log("changeGameState", state);
    const lastState = gameObject.state;
    gameObject.state = state;
    switch (state) {
        case undefined:
            //Audio
            audioPlayer.play(0); // Lobby music
            //Buttons
            $id("button-play-again").style.display = "none";
            break;

        case "pending":
            //Audio
            audioPlayer.play(0); // Lobby music
            // Buttons
            $id("button-play-again").style.display = "none";
            // Main Info text
            if (gameObject.wsConnection) {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "connected-waiting");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectator-waiting");
            } else {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "pending");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectator-connect");
            }
            break;

        case "countdown":
            // Audio
            audioPlayer.play(gameObject.mapId);
            if (lastState === "paused")
                audioPlayer.playSound("unpause");
            // Buttons
            $id("button-play-again").style.display = "none";
            // Show game field
            toggleGamefieldVisible(true);
            // Update player states
            gameObject.playerLeft.state = "ongoing";
            gameObject.playerRight.state = "ongoing";
            break;

        case "ongoing":
            // Buttons
            $id("button-play-again").style.display = "none";
            // Update player states
            gameObject.playerLeft.state = "ongoing";
            gameObject.playerRight.state = "ongoing";
            break;

        case "paused":
            // Audio
            audioPlayer.play(0); // Lobby music
            if (lastState === "ongoing")
                audioPlayer.playSound("pause");
            // Buttons
            $id("button-play-again").style.display = "none";
            // Hide game field
            toggleGamefieldVisible(false);
            // Main Info text
            if (gameObject.wsConnection){
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "connected-waiting");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectator-waiting");
            } else {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "paused-connect");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectator-connect");
            }
            break;

        case "finished":
            // Audio
            audioPlayer.play(0); // Lobby music
            if (lastState === "ongoing")
                audioPlayer.playSound("gameover");
            // Buttons
            $id("button-play-again").style.display = "block";
            // Hide game field
            toggleGamefieldVisible(false);
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "finished");
            // Update the player states
            gameObject.playerLeft.state = "finished"
            gameObject.playerRight.state = "finished"
            break;

        default:
            console.warn("FE doen't know what to do with this state:", state);
    }
    drawPlayersState();
}

function drawPlayerState(playerSide) {
    // Side should be "playerLeft" or "playerRight"
    // state can be "waiting", "ready", "ongoing", "finished"
    let playerSideDash = "player-left";
    if (playerSide === "playerRight")
        playerSideDash = "player-right";
    if (gameObject[playerSide].state === undefined) {
        // Hide everything
        $id(playerSideDash + "-state").innerHTML = "";
        $id(playerSideDash + "-state-spinner").style.display = "none";
        $id(playerSideDash + "-powerups-status").style.display = "none";
    } else if (gameObject[playerSide].state === "waiting") {
        // Show spinner; Hide message and powerup states
        $id(playerSideDash + "-state").innerHTML = "";
        $id(playerSideDash + "-state-spinner").style.display = "block";
        $id(playerSideDash + "-powerups-status").style.display = "none";
    } else if (gameObject[playerSide].state === "ready") {
        // Show message; Hide spinner and powerup states
        $id(playerSideDash + "-state").innerText = translate("game", "ready");
        $id(playerSideDash + "-state-spinner").style.display = "none";
        $id(playerSideDash + "-powerups-status").style.display = "none";
    } else if (gameObject[playerSide].state === "ongoing") {
        // Show powerup states; Hide message and spinner
        $id(playerSideDash + "-state").innerHTML = "";
        $id(playerSideDash + "-state-spinner").style.display = "none";
        $id(playerSideDash + "-powerups-status").style.display = "flex";
        // Set the powerup images
        const imgPathPre = `${window.origin}/assets/game/icons/powerup-`;
        console.warn("path:", imgPathPre + gameObject[playerSide].powerupBig + "-big.png");
        $id(playerSideDash + "-powerups-big").src = imgPathPre + gameObject[playerSide].powerupBig + "-big.png";
        $id(playerSideDash + "-powerups-slow").src = imgPathPre + gameObject[playerSide].powerupSlow + "-slow.png";
        $id(playerSideDash + "-powerups-fast").src = imgPathPre + gameObject[playerSide].powerupFast + "-fast.png";
    } else if (gameObject[playerSide].state === "finished") {
        // Show score; Hide spinner and powerup states
        $id(playerSideDash + "-state").innerText = gameObject[playerSide].points;
        $id(playerSideDash + "-state-spinner").style.display = "none";
        $id(playerSideDash + "-powerups-status").style.display = "none";
        // Also add the winner / looser class
        if (gameObject[playerSide].result === "won") {
            $id(playerSideDash + "-username").classList.remove("user-card-looser");
            $id(playerSideDash + "-username").classList.add("user-card-winner");
        }
        else {
            $id(playerSideDash + "-username").classList.remove("user-card-winner");
            $id(playerSideDash + "-username").classList.add("user-card-looser");
        }
    }
}

export function drawPlayersState() {
    drawPlayerState("playerLeft");
    drawPlayerState("playerRight");
}

/* export function updateReadyStateNodes() {
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
            console.log("result", gameObject.playerLeft.result);
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
            console.log("result", gameObject.playerRight.result);
            if (gameObject.playerRight.result === "won") {
                $id("user-card-player-right").classList.remove("user-card-looser");
                $id("user-card-player-right").classList.add("user-card-winner");
            } else {
                $id("user-card-player-right").classList.remove("user-card-winner");
                $id("user-card-player-right").classList.add("user-card-looser");
            }

        }
} */

export function updateReadyStatefromWS(readyStateObject) {
    let gameCountdownIntervalId = undefined;

    // Remove paused banner:
    $id("game-view-middle-side-container-top-text").innerText = "";

    // To stop a potential ongoing game we need to:
    endGameLoop();

    gameObject.playerLeft.state = readyStateObject.playerLeft ? "ready" : "waiting";
    gameObject.playerRight.state = readyStateObject.playerRight ? "ready" : "waiting";
    //console.log("updateReadyState", gameObject.playerLeft.state, gameObject.playerRight.state);
    drawPlayersState();

    if (readyStateObject.startTime) {
        animateImage("game-countdown-image", "pulsate", "1s", "infinite");
        changeGameState("countdown");
        startGameLoop();

        gameCountdownIntervalId = setInterval((startTime) => {
            const now = new Date();
            let diff = Math.floor((startTime - now) / 1000);
            console.log("diff", diff);
            gameCountdownImage(diff);
            if (diff <= 0) {
                clearInterval(gameCountdownIntervalId);
                return;
            }

            /* if (diff == 3) {
                console.log("Fading in map image");
                showGame(true);
                setTimeout(() => {
                    removeImageAnimation("game-view-map-image");
                }, 3000);
            } */


        }, 1000, new Date(readyStateObject.startTime));
    }
}

export function updateGameObjects(beMessage) {
    // The first time we get the state ongoing we need to set it
    if ( beMessage?.gameData?.state === "ongoing" && gameObject.state !== "ongoing")
        changeGameState("ongoing");
    gameObject.state = beMessage?.gameData?.state;
    gameObject.sound = beMessage?.gameData?.sound;
    gameObject.playerLeft.points = beMessage?.playerLeft?.points;
    gameObject.playerLeft.result = beMessage?.playerLeft?.result;
    gameObject.playerLeft.size = percentageToPixels('y', beMessage?.playerLeft?.paddleSize);
    gameObject.playerLeft.pos = percentageToPixels('y', beMessage?.playerLeft?.paddlePos) - gameObject.playerLeft.size / 2 + gameObject.borderStrokeWidth; // Center the paddle
    gameObject.playerLeft.powerupBig = beMessage?.playerLeft?.powerupBig;
    gameObject.playerLeft.powerupSlow = beMessage?.playerLeft?.powerupSlow;
    gameObject.playerLeft.powerupFast = beMessage?.playerLeft?.powerupFast;
    gameObject.playerRight.points = beMessage?.playerRight?.points;
    gameObject.playerRight.result = beMessage?.playerRight?.result;
    gameObject.playerRight.size = percentageToPixels('y', beMessage?.playerRight?.paddleSize);
    gameObject.playerRight.pos = percentageToPixels('y', beMessage?.playerRight?.paddlePos) - gameObject.playerRight.size / 2 + gameObject.borderStrokeWidth; // Center the paddle
    gameObject.playerRight.powerupBig = beMessage?.playerRight?.powerupBig;
    gameObject.playerRight.powerupSlow = beMessage?.playerRight?.powerupSlow;
    gameObject.playerRight.powerupFast = beMessage?.playerRight?.powerupFast;
    gameObject.ball.posX = percentageToPixels('x', beMessage?.ball?.posX) + gameObject.borderStrokeWidth;
    gameObject.ball.posY = percentageToPixels('y', beMessage?.ball?.posY) + gameObject.borderStrokeWidth;
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

















const gameCountdownImage = (timeDiff) => {
    console.warn("!gameCountdownImage", timeDiff);
    const gameCountdownImage = $id("game-countdown-image");
    const basePath = `${window.origin}/assets/game/countdown/`;
    gameCountdownImage.src = basePath + timeDiff + ".png";
    gameCountdownImage.style.display = "block";
    audioPlayer.playSound("beep1");
    if (!timeDiff) {
        audioPlayer.playSound("beep2");
        gameCountdownImage.style.display = "none";
    }
}