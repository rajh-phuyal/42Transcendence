import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import router from '../../navigation/router.js';
import { $id } from '../../abstracts/dollars.js';
import { gameObject } from './objects.js';
import { translate } from '../../locale/locale.js';
import { animateImage } from './loop.js';
import { endGameLoop } from './loop.js';
import { startGameLoop} from './loop.js';
import { audioPlayer } from '../../abstracts/audio.js';
import { toggleGamefieldVisible, gameRender } from './render.js';
import { loadTimestamp } from '../../abstracts/timestamps.js';

// Object to track active deadline of game
const deadlineTimers = {};

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
    // In case the countdown is still running, we need to stop it
    if (gameObject.countDownInterval) {
        clearInterval(gameObject.countDownInterval);
        gameObject.countDownInterval = undefined;
        $id("game-countdown-image").style.display = "none";
    }

    // console.log("changeGameState", state);
    const lastState = gameObject.state;
    gameObject.state = state;
    switch (state) {
        case undefined:
            //Audio
            audioPlayer.playMusic("lobbyGame");
            //Buttons
            $id("button-play-again").style.display = "none";
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = "";
            // Show game field
            toggleGamefieldVisible(false);
            toggleDeadline(false);
            break;

        case "pending":
            //Audio
            audioPlayer.playMusic("lobbyGame");
            // Buttons
            $id("button-play-again").style.display = "none";
            // Show game field
            toggleGamefieldVisible(false);
            // Main Info text
            if (gameObject.wsConnection) {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "connectedWaiting");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectatorWaiting");
            } else {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "pending");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectatorConnect");
            }
            toggleDeadline(true);
            break;

        case "countdown":
            if (!gameObject.wsConnection){
                changeGameState("pending");
                break;
            }
            // Audio
            audioPlayer.playMusic(gameObject.mapName);
            if (lastState === "paused")
                audioPlayer.playSound("unpause");
            // Buttons
            $id("button-play-again").style.display = "none";
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = "";
            // Show game field
            toggleGamefieldVisible(true);
            // Update player states
            gameObject.playerLeft.state = "ongoing";
            gameObject.playerRight.state = "ongoing";
            toggleDeadline(false);
            break;

        case "ongoing":
            // Buttons
            $id("button-play-again").style.display = "none";
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = "";
            // Show game field
            toggleGamefieldVisible(true);
            // Update player states
            gameObject.playerLeft.state = "ongoing";
            gameObject.playerRight.state = "ongoing";
            toggleDeadline(false);
            break;

        case "paused":
            // Audio
            audioPlayer.playMusic("lobbyGame");
            if (lastState === "ongoing")
                audioPlayer.playSound("pause");
            // Buttons
            $id("button-play-again").style.display = "none";
            // Hide game field
            toggleGamefieldVisible(false);
            // Main Info text
            if (gameObject.wsConnection){
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "connectedWaiting");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectatorWaiting");
            } else {
                if(gameObject.clientIsPlayer)
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "pausedConnect");
                else
                    $id("game-view-middle-side-container-top-text").innerText = translate("game", "spectatorConnect");
            }
            toggleDeadline(true);
            break;

        case "finished":
            // Audio
            audioPlayer.playMusic("lobbyGame");
            if (lastState === "ongoing")
                audioPlayer.playSound("gameover");
            // Buttons
            if (!gameObject.tournamentId)
                $id("button-play-again").style.display = "block";
            $id("button-quit-game").style.display = "none";
            // Hide game field
            toggleGamefieldVisible(false);
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "finished");
            // Update the player states
            gameObject.playerLeft.state = "finished"
            gameObject.playerRight.state = "finished"
            // If game is part of tournament and previous state was ongoing, redirect to tournament
            if (gameObject.tournamentId && lastState === "ongoing") {
                $id("game-view-middle-side-container-top-text").innerText = translate("game", "redirTournament");
                setTimeout(() => {
                    router('/tournament', {id: gameObject.tournamentId});
                }, 5000);
            }
            toggleDeadline(false);
            break;

        case "quited":
            // Audio
            audioPlayer.playMusic("lobbyGame");
            if (lastState === "ongoing")
                audioPlayer.playSound("gameover");
            // Buttons
            $id("button-play-again").style.display = "block";
            $id("button-quit-game").style.display = "none";
            // Hide game field
            toggleGamefieldVisible(false);
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "quited");
            // Update the player states
            gameObject.playerLeft.state = "finished"  // Since the behaviour is the same as finished
            gameObject.playerRight.state = "finished" // Since the behaviour is the same as finished
            break;

        case "aboutToBeDeleted":
            // Audio
            audioPlayer.playMusic("lobbyGame");
            if (lastState === "ongoing")
                audioPlayer.playSound("no");
            // Main Info text
            $id("game-view-middle-side-container-top-text").innerText = translate("game", "deleted");
            // Sleep for 10 seconds and then redirect to the lobby
            setTimeout(() => {
                router('/');
            }, 5000);
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
        const imgPathPre = `${window.origin}/assets/icons_128x128/icon_powerup-`;
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
            $id(playerSideDash + "-avatar").classList.remove("user-card-looser");
            $id(playerSideDash + "-avatar").classList.add("user-card-winner");
        }
        else if (gameObject[playerSide].result === "lost") {
            $id(playerSideDash + "-username").classList.remove("user-card-winner");
            $id(playerSideDash + "-username").classList.add("user-card-looser");
            $id(playerSideDash + "-avatar").classList.remove("user-card-winner");
            $id(playerSideDash + "-avatar").classList.add("user-card-looser");
        } else
            console.log("finished game but I don't know if I won or lost: ", gameObject[playerSide].result);
    }
}

export function drawPlayersState() {
    drawPlayerState("playerLeft");
    drawPlayerState("playerRight");
}

export function updateReadyStatefromWS(readyStateObject) {
    // Remove paused banner:
    $id("game-view-middle-side-container-top-text").innerText = "";

    // To stop a potential ongoing game we need to:
    endGameLoop();

    gameObject.playerLeft.state = readyStateObject.playerLeft ? "ready" : "waiting";
    gameObject.playerRight.state = readyStateObject.playerRight ? "ready" : "waiting";
    //console.log("updateReadyState", gameObject.playerLeft.state, gameObject.playerRight.state);
    drawPlayersState();

    // If we already have the countdown we need to reset it first
    if (gameObject.state === "countdown" || gameObject.state === "ongoing") {
        clearInterval(gameObject.countDownInterval);
        gameObject.countDownInterval = undefined;
        $id("game-countdown-image").style.display = "none";
        changeGameState("pending");
    }

    if (readyStateObject.startTime) {
        animateImage("game-countdown-image", "pulsate", "1s", "infinite");
        changeGameState("countdown");
        startGameLoop();
        gameObject.countDownInterval = setInterval((startTime) => {
            const now = new Date();
            let diff = Math.floor((startTime - now) / 1000);
            gameCountdownImage(diff);
            if (diff <= 0) {
                clearInterval(gameObject.countDownInterval);
                return;
            }

            /* if (diff == 3) {
                console.log("Fading in map image");
                showGame(true);
                setTimeout(() => {
                    removeImageAnimation("game-view-map-image");
                }, 3000);
            } */


        }, 1000, loadTimestamp(readyStateObject.startTime, null));
    }
}

export function updateGameObjects(beMessage) {
    // For a viewer who enters an ongoing game we need to change the state!
    if (!gameObject.clientIsPlayer) {
        if (gameObject.state !== beMessage?.gameData?.state) {
            changeGameState(beMessage?.gameData?.state);
            if (gameObject.state === "countdown" || gameObject.state === "ongoing")
                startGameLoop();
        }
    }

    // The first time we get the state ongoing we need to set it
    if ( beMessage?.gameData?.state === "ongoing" && gameObject.state !== "ongoing")
        changeGameState("ongoing");
    gameObject.state        = beMessage?.gameData?.state;
    gameObject.sound        = beMessage?.gameData?.sound;
    gameObject.deadline     = beMessage?.gameData?.deadline;
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

function paddleMovementNormalizer(playerObject, upKey, downKey) {
    if (upKey && !downKey)
        playerObject.paddleMovement = '-';
    else if (!upKey && downKey)
        playerObject.paddleMovement = '+';
    else if (!upKey && !downKey)
        playerObject.paddleMovement = '0';
}

export function sendPlayerInput() {

    paddleMovementNormalizer(gameObject.playerInputLeft, gameObject.keyStrokes.w, gameObject.keyStrokes.s);
    paddleMovementNormalizer(gameObject.playerInputRight, gameObject.keyStrokes.o, gameObject.keyStrokes.l);
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
    const gameCountdownImage = $id("game-countdown-image");
    const basePath = `${window.origin}/assets/images/game/countdown/`;
    gameCountdownImage.src = basePath + timeDiff + ".png";
    gameCountdownImage.style.display = "block";
    audioPlayer.playSound("beep1");
    if (!timeDiff) {
        audioPlayer.playSound("beep2");
        gameCountdownImage.style.display = "none";
    }
}

function toggleDeadline(visible) {
    stopGameDeadline(1);
    const countdown = $id("game-view-deadline");
    if (visible){
        if (gameObject.deadline){
            const container = $id("game-view-deadline");
            startGameDeadline(container, 1, gameObject.deadline);
            container.title = translate("game", "tooltipHurryUp");
            countdown.style.display = "flex";
            return ;
        }
    }

    if (!visible){
        stopGameDeadline(1);
        countdown.style.display = "none";
    }
}

/* THE FUNCTIONS BELOW ARE COPIED FROM TOURNAMENT
    IF WE HAVE TIME WE COULD SIMPLYFY THEM HERE SINCE WE ONLY HAVE ONE GAME
*/
function startGameDeadline(container, id, deadlineISO) {
    function updateGameDeadline() {
        const now = moment.utc().local();
        const deadline = moment.utc(deadlineISO).local();
        let remainingSeconds = Math.floor((deadline - now) / 1000);
        if (remainingSeconds >= 0) {
            container.textContent = remainingSeconds;
            deadlineTimers[id] = setTimeout(updateGameDeadline, 1000);
        } else if (remainingSeconds < -6) {
            // If the deadline is over 6 seconds ago, we reload the game or redir to tournament lobby1
            if(gameObject.tournamentId)
                router(`/tournament`, { id: gameObject.tournamentId });
            // This else triggers a reload loop!!!
            //else
                //router(`/game`, { id: gameObject.gameId });
            // Not sure if this is needed after the router call
            stopGameDeadline(id);
        } else {
            container.textContent = "0"; // Stop deadline at 0
            deadlineTimers[id] = setTimeout(updateGameDeadline, 1000);
        }
    }
    // Start deadline
    updateGameDeadline();
}
function stopGameDeadline(gameid) {
    // Stop the deadline for the specific game by clearing the timeout
    if (deadlineTimers[gameid]) {
        clearTimeout(deadlineTimers[gameid]);
        delete deadlineTimers[gameid];
    }
}
// Function to stop and clear all deadline
export function clearAllGameDeadlines() {
    Object.values(deadlineTimers).forEach(clearTimeout);
    Object.keys(deadlineTimers).forEach((key) => delete deadlineTimers[key]);
}