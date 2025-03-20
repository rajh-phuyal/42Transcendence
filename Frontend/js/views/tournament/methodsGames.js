import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData } from "./objects.js";
import router from "../../navigation/router.js";

/* This function will fully deal with the games stored in:
    tournamentData.all.tournamentGames
*/
export function updateGames() {
    // Delete all games
    $id("container-games-upcoming").innerHTML = "";
    $id("container-games-finished").innerHTML = "";
    // Create all games // TODO: split them for the views
    for (let game of tournamentData.all.tournamentGames)
        createGameCard(game);
}

function createGameCard(game) {
    console.log("game", game);
    /*
    The backend crreates all 4 finals at once as soon as round robin is over.
    Therefore the backend doesn't know who is going to be playerLeft and playerRight.
    The frontend will handle this by checking if the player not null
     */
    if(game.playerLeft === null || game.playerRight === null)
        return ;

    const template = $id("tournament-game-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-game-card-container");
    container.setAttribute("gameid", game.id)
    template.querySelector(".tournament-game-card-player1-avatar").src = window.origin + "/media/avatars/" + game.playerLeft.avatarUrl;
    template.querySelector(".tournament-game-card-player2-avatar").src = window.origin + "/media/avatars/" + game.playerRight.avatarUrl;
    template.querySelector(".tournament-game-card-player1-username").textContent = game.playerLeft.username;
    template.querySelector(".tournament-game-card-player2-username").textContent = game.playerRight.username;
    template.querySelector(".tournament-game-card-spinner").style.display = "none";
    template.querySelector(".tournament-game-card-player1-winner-tag").style.display = "none";
    template.querySelector(".tournament-game-card-player2-winner-tag").style.display = "none";
    // Add click listener
    container.addEventListener("click", gameCardCallback);

    if (game.state === "pending")
        template.querySelector(".tournament-game-card-score").textContent = "VS"; // TODO: translate
    else
        template.querySelector(".tournament-game-card-score").textContent = game.playerLeft.points + "-" + game.playerRight.points;

    if (game.state === "finished" || game.state === "quited")
        $id("container-games-finished").appendChild(container);
    else
        $id("container-games-upcoming").appendChild(container);

    if (!game.deadline)
        container.style.display = "none";

}

function gameCardCallback(event) {
    const gameId = event.currentTarget.getAttribute("gameid");
    router(`/game`, { id: gameId });
}




/* BELOW IS OLD CODE!!! */

function moveGameCardToHistory(gameId) {
    $id("tournament-history-container").appendChild($id("tournament-game-" + gameId));
}

export function updateGameCardScore(gameObject) {
    $id("tournament-game-" + gameId).querySelector(".tournament-game-card-score").textContent = gameObject.player1.points + "-" + gameObject.player2.points;
}

export function gameUpdateScore(gameObject) {
    $id("tournament-game-" + gameObject.gameId).querySelector(".tournament-game-card-score").textContent = gameObject.newScore;
}

export function gameUpdateState(gameObject) {
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


export function updateGameCard(gameObject) {
    console.log("game object:", gameObject);
    if (!$id("tournament-game-" + gameObject.id))
        createGameCard(gameObject);
    else
        gameUpdateState(gameObject);
    if (gameObject.deadline)
        $id("tournament-game-" + gameObject.id).style.display = "flex";
}



export function createGameList(games) {
    console.log("Creating game list with data: ", games);
    for (let element of games) {
        createGameCard(element);
    }
}

