import { tournamentData } from "./objects.js";
import { translate } from '../../locale/locale.js';
import { $id } from "../../abstracts/dollars.js";
import router from "../../navigation/router.js";
import $store from '../../store/store.js';

// Object to track active countdowns of games
const deadlineTimers = {};

/* This function will fully deal with the games stored in:
    tournamentData.all.tournamentGames
*/
export function updateGames() {
    // Create all games
    for (let game of tournamentData.tournamentGames) {
        // Find game card in upcoming tab
        let container = $id("container-games-upcoming-list").querySelector(`[gameid="${game.id}"]`);
        // Find game card in finished tab
        if(!container)
            container = $id("container-games-finished-list").querySelector(`[gameid="${game.id}"]`);
        // If the game card doesn't exist, create it
        if(!container)
            container = createTemplateGameCard(game);
        // Update the game card
        updateGameCard(container, game);
    }
}

/* This will create the html node */
function createTemplateGameCard(game) {
    // This is for the final games wich come without the players first
    if (!game.playerLeft || !game.playerRight)
        return ;
    const template = $id("tournament-game-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-game-card-container");
    // Store the game id
    container.setAttribute("gameid", game.id)
    container.setAttribute("player-left-id", game.playerLeft.id);
    container.setAttribute("player-right-id", game.playerRight.id);
    // Add click listener
    container.addEventListener("click", gameCardCallback);
    // Set the player's data
    template.querySelector(".tournament-game-card-player-left-avatar").src = window.origin + "/media/avatars/" + game.playerLeft.avatar;
    template.querySelector(".tournament-game-card-player-right-avatar").src = window.origin + "/media/avatars/" + game.playerRight.avatar;
    template.querySelector(".tournament-game-card-player-left-username").textContent = game.playerLeft.username;
    template.querySelector(".tournament-game-card-player-right-username").textContent = game.playerRight.username;
    // Always add it to the upcoming tab the updateGameCard will move it to the finished tab if needed
    $id("container-games-upcoming-list").appendChild(container);

    // Return the container
    return container;
}

function updateGameCard(container, game) {
    // This is for the final games wich come without the players first
    if (!game.playerLeft || !game.playerRight)
        return ;
    // Adjust the styling according to the state
    if (game.state === "pending") {
        // STATE: PENDING
        if (game.deadline) {
            container.style.display = "grid";
            container.title = translate("tournament", "tooltipGameDeadline");
            startGameDeadline(container, game.id, game.deadline);
            // Animate the card
            if (tournamentData.tournamentInfo && tournamentData.tournamentInfo.local) {
                // Local Tournament so only animate if client is admin
                if (tournamentData.clientRole === "admin")
                    container.style.animation = "pulse-game-card 2s infinite";
            } else {
                // Remote Tournament so animate if the user is part of the game
                if (container.getAttribute("player-left-id") == $store.fromState("user").id || container.getAttribute("player-right-id") == $store.fromState("user").id)
                    container.style.animation = "pulse-game-card 2s infinite";
            }
        }
        else
            container.style.display = "none";
    }
    else if (game.state === "countdown" || game.state === "ongoing" || game.state === "paused") {
        // STATE: COUNTDOWN, ONGOING, PAUSED
        // remove the deadline if it exists
        stopGameDeadline(game.id);
        container.style.display = "grid";
        if(game.state === "paused") {
            container.title = translate("tournament", "tooltipGamePaused");
            startGameDeadline(container, game.id, game.deadline);
        } else {
            container.title = translate("tournament", "tooltipGameOngoing");
        }
        // Animate the score change
        const scoreContainer = container.querySelector(".tournament-game-card-score");
        const newScore = game.playerLeft.points + "-" + game.playerRight.points;
        if(newScore !== scoreContainer.textContent) {
            // console.warn("Animate score change");
            scoreContainer.textContent = newScore;
            triggerScoreAnimation(scoreContainer);
        }
    }
    else {
        // STATE: FINISHED, QUITED
        // remove the deadline if it exists
        stopGameDeadline(game.id);
        container.style.display = "grid";
        container.title = translate("tournament", "tooltipGameFinished");
        // Animate the score change
        const scoreContainer = container.querySelector(".tournament-game-card-score");
        const newScore = game.playerLeft.points + "-" + game.playerRight.points;
        // Clean up old animation
        scoreContainer.style.animation = "none";
        scoreContainer.offsetHeight;
        scoreContainer.style.removeProperty("animation");
        // Update the score
        if(newScore !== scoreContainer.textContent)
            scoreContainer.textContent = newScore;
        // Highlight the winner
        if (game.playerLeft.result === "won") {
            container.querySelector(".tournament-game-card-player-left-avatar").style.filter    = "brightness(1)";
            container.querySelector(".tournament-game-card-player-right-avatar").style.filter   = "brightness(0.5)";
            container.querySelector(".tournament-game-card-player-left-username").style.color   = "black";
            container.querySelector(".tournament-game-card-player-right-username").style.color  = "grey";
        }
        else {
            container.querySelector(".tournament-game-card-player-left-avatar").style.filter    = "brightness(0.5)";
            container.querySelector(".tournament-game-card-player-right-avatar").style.filter   = "brightness(1)";
            container.querySelector(".tournament-game-card-player-left-username").style.color   = "grey";
            container.querySelector(".tournament-game-card-player-right-username").style.color  = "black";
        }
    }

    // If finsihsed or quited move to the finished tab
    if(game.state === "finished" || game.state === "quited") {
        container.style.animation = "none"; // Remove the pulse animation
        $id("container-games-finished-list").appendChild(container);
    }
    // console.log("Updated game card with data: ", game);
}

function gameCardCallback(event) {
    const gameId = event.currentTarget.getAttribute("gameid");
    router(`/game`, { id: gameId });
}

function startGameDeadline(gameCardContainer, gameid, deadlineISO) {
    const deadlineElement = gameCardContainer.querySelector(".tournament-game-card-score");

    function updateGameDeadline() {
        const now = moment.utc().local();
        const deadline = moment.utc(deadlineISO).local();
        let remainingSeconds = Math.max(0, Math.floor((deadline - now) / 1000));
        deadlineElement.textContent = remainingSeconds;
        if (remainingSeconds > 0) {
            deadlineTimers[gameid] = setTimeout(updateGameDeadline, 1000);
        } else {
            deadlineElement.textContent = "0"; // Stop deadline at 0
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

// Used to trigger the animation of the score change
function triggerScoreAnimation(scoreContainer) {
    // FUTURE: this is not working super well. The animation is not always triggered but it'snice to have and not critical
    scoreContainer.style.animation = 'none';
    scoreContainer.offsetHeight;
    // Apply the animation (again)
    scoreContainer.style.animation = "pulse-score 500ms ease-in-out";
    // Listen for the animation to end and reset it
    scoreContainer.addEventListener('animationend', function resetAnimation() {
        scoreContainer.removeEventListener('animationend', resetAnimation);
        scoreContainer.style.animation = 'none';
        scoreContainer.offsetHeight;
        console.warn("Score animation ended");
    });
}