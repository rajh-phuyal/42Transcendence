import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData as data } from "./objects.js";
import router from "../../navigation/router.js";

// Object to track active countdowns of games
const countdownTimers = {};

/* This function will fully deal with the games stored in:
    tournamentData.all.tournamentGames
*/
export function updateGames() {
    // Create all games
    for (let game of data.tournamentGames) {
        // Find game card in upcoming tab
        let container = $id("container-games-upcoming").querySelector(`[gameid="${game.id}"]`);
        // Find game card in finished tab
        if(!container)
            container = $id("container-games-finished").querySelector(`[gameid="${game.id}"]`);
        // If the game card doesn't exist, create it
        if(!container)
            container = createTemplateGameCard(game);
        // Update the game card
        updateGameCard(container, game);
    }
}

/* This will create the html node */
function createTemplateGameCard(game) {
    /* TODO: make this work again! */
    /*
    The backend creates all 4 finals at once as soon as round robin is over.
    Therefore the backend doesn't know who is going to be playerLeft and playerRight.
    The frontend will handle this by checking if the player not null
     */
    // if(game.playerLeft === null || game.playerRight === null)
    //     return ;
    const template = $id("tournament-game-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-game-card-container");
    // Store the game id
    container.setAttribute("gameid", game.id)
    // Add click listener
    container.addEventListener("click", gameCardCallback);
    // Set the player's data
    template.querySelector(".tournament-game-card-player-left-avatar").src = window.origin + "/media/avatars/" + game.playerLeft.avatarUrl;
    template.querySelector(".tournament-game-card-player-right-avatar").src = window.origin + "/media/avatars/" + game.playerRight.avatarUrl;
    template.querySelector(".tournament-game-card-player-left-username").textContent = game.playerLeft.username;
    template.querySelector(".tournament-game-card-player-right-username").textContent = game.playerRight.username;
    // Always add it to the upcoming tab the updateGameCard will move it to the finished tab if needed
    $id("container-games-upcoming").appendChild(container);

    // Return the container
    console.log("Created game card with data: ", game);
    return container;
}

function updateGameCard(container, game) {
    // Adjust the styling according to the state
    if (game.state === "pending") {
        if (game.deadline) {
            container.style.display = "grid";
            container.title = "Hurrry up! The game is only open for a limited time!"; // TODO: translate
            container.querySelector(".spin").style.display = "flex";
            startGameCountdown(container, game.id, game.deadline);
        }
        else
            container.style.display = "none";
    }
    else if (game.state === "countdown" || game.state === "ongoing" || game.state === "paused") {
        container.style.display = "grid";
        container.title = "The game is ongoing!"; // TODO: translate
        container.querySelector(".spin").style.display = "flex";
        container.querySelector(".tournament-game-card-score").textContent = game.playerLeft.points + "-" + game.playerRight.points;
    }
    else {
        // Sate is finished or quited
        container.style.display = "grid";
        container.title = "The game is finished!"; // TODO: translate
        container.querySelector(".spin").style.display = "none";
        container.querySelector(".tournament-game-card-score").textContent = game.playerLeft.points + "-" + game.playerRight.points;
        // Highlight the winner
        if (game.playerLeft.result === "won") {
            container.querySelector(".tournament-game-card-player-left-avatar").style.filter    = "brightness(1.5)";
            container.querySelector(".tournament-game-card-player-right-avatar").style.filter   = "brightness(0.5)";
        }
        else {
            container.querySelector(".tournament-game-card-player-left-avatar").style.filter    = "brightness(0.5)";
            container.querySelector(".tournament-game-card-player-right-avatar").style.filter   = "brightness(1.5)";
        }
    }

    // If finsihsed or quited move to the finished tab
    if(game.state === "finished" || game.state === "quited")
        $id("container-games-finished").appendChild(container);
    console.log("Updated game card with data: ", game);
}

function gameCardCallback(event) {
    const gameId = event.currentTarget.getAttribute("gameid");
    router(`/game`, { id: gameId });
}

function startGameCountdown(gameCardContainer, gameid, deadlineISO) {
    const countdownElement = gameCardContainer.querySelector(".tournament-game-card-score");

    function updateGameCountdown() {
        const now = moment.utc();
        const deadline = moment.utc(deadlineISO);
        let remainingSeconds = Math.max(0, Math.floor((deadline - now) / 1000));
        countdownElement.textContent = remainingSeconds;
        if (remainingSeconds > 0) {
            countdownTimers[gameid] = setTimeout(updateGameCountdown, 1000);
        } else {
            countdownElement.textContent = "0"; // Stop countdown at 0
        }
    }
    // Start countdown
    updateGameCountdown();
}

// Function to stop and clear all countdowns
export function clearAllGameCountdowns() {
    Object.values(countdownTimers).forEach(clearTimeout);
    Object.keys(countdownTimers).forEach((key) => delete countdownTimers[key]);
}

















































/* BELOW IS OLD CODE!!! */


function updateGameCardScore(gameObject) {
    $id("tournament-game-" + gameId).querySelector(".tournament-game-card-score").textContent = gameObject.player1.points + "-" + gameObject.player2.points;
}

function gameUpdateScore(gameObject) {
    $id("tournament-game-" + gameObject.gameId).querySelector(".tournament-game-card-score").textContent = gameObject.newScore;
}

function gameUpdateState(gameObject) {
    const gameCard = $id("tournament-game-" + gameObject.id);

    gameCard.querySelector(".tournament-game-card-spinner").style.display = "none";

    if (gameObject.state === "pending") {
        gameCard.querySelector(".tournament-game-card-score").textContent = "VS";
        return ;
    }

    gameCard.querySelector(".tournament-game-card-score").textContent = gameObject.playerLeft.points + "-" + gameObject.playerRight.points;

    if (gameObject.state === "paused")
        gameCard.querySelector(".tournament-game-card-spinner").style.display = "flex";
    else if (gameObject.state === "finished" || gameObject.state === "quited") {
        moveGameCardToHistory(gameObject.id);
    }
}





function createGameList(games) {
    console.log("Creating game list with data: ", games);
    for (let element of games) {
        createTemplateGameCard(element);
    }
}

