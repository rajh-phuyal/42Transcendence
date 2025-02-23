import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData } from "./objects.js";
import router from "../../navigation/router.js";

export function buildView(tournamentState) {

    console.log("state:", tournamentState);

    let flexDivs;
    let hideDivs;

    if (tournamentState === "setup") {
        flexDivs = $class("tournament-setup")
        hideDivs = $class("tournament-ongoing")
    }
    else if (tournamentState === "delete") {
        router('/home');
        return ;
    }
    else {
        flexDivs = $class("tournament-ongoing")
        hideDivs = $class("tournament-setup")
    }

    
    for (let element of flexDivs) {
        console.log("flexing:", element.getAttribute("id"));
        element.style.display = 'flex';
    }
    for (let element of hideDivs) {
        console.log("hiding:", element.getAttribute("id"));
        element.style.display = 'none';
    }

    if (tournamentState === "finished") {
        $id("tournament-middle-bottom-current-game-button").style.display = "none"; 
        $id("tournament-games-do-come-button").style.display = "none";
        $id("tournament-middle-bottom-subscribe-start-button").style.display = "none";
        $id("tournament-quit-cancel-button").style.display = "none";
        $id("tournament-current-games-container").style.display = "none"; 
        $id("tournament-rank-container").style.display = "flex"; 
        $id("tournament-history-container").style.display = "none"; 
        return ;
        
    }

    $id("tournament-rank-container").style.display = "none"; 
    $id("tournament-history-container").style.display = "none"; 
}

export function createPlayerCard(playerObject) {

    console.log("player", playerObject);

    tournamentData.playersIds.push(playerObject.id);

    const template = $id("tournament-players-list-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-players-list-player-card");

    container.setAttribute("id", "tournament-players-list-player" + playerObject.id)

    if (playerObject.avatarUrl)
        template.querySelector(".tournament-players-list-player-card-avatar").src = window.origin + "/media/avatars/" + playerObject.avatarUrl;
    else
    template.querySelector(".tournament-players-list-player-card-avatar").style.display = "none";
    template.querySelector(".tournament-players-list-player-card-username").textContent = playerObject.username;

    if (playerObject.state === "pending")
        container.style.backgroundColor = "grey";

    $id("tournament-players-list-container").appendChild(container);
}

export function removePlayerCard(playerId) {
    $id("tournament-players-list-player" + playerId).remove();
}

export function changePlayerCardToAccepted(playerId) {
    $id("tournament-players-list-player" + playerId).style.backgroundColor = "white";
}

export function createGameCard(gameObject) {

    console.log("player", gameObject);

    const template = $id("tournament-game-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-game-card-container");

    container.setAttribute("id", "tournament-game-" + gameObject.id)
    template.querySelector(".tournament-game-card-player1-avatar").src = window.origin + "/media/avatars/" + gameObject.playerLeft.avatarUrl;
    template.querySelector(".tournament-game-card-player2-avatar").src = window.origin + "/media/avatars/" + gameObject.playerRight.avatarUrl;
    template.querySelector(".tournament-game-card-player1-username").textContent = gameObject.playerLeft.username;
    template.querySelector(".tournament-game-card-player2-username").textContent = gameObject.playerRight.username;
    template.querySelector(".tournament-game-card-spinner").style.display = "none";
    template.querySelector(".tournament-game-card-player1-winner-tag").style.display = "none";
    template.querySelector(".tournament-game-card-player2-winner-tag").style.display = "none";

    if (gameObject.state === "pending")
        template.querySelector(".tournament-game-card-score").textContent = "VS";
    else
        template.querySelector(".tournament-game-card-score").textContent = gameObject.playerLeft.points + "-" + gameObject.playerRight.points;

    if (gameObject.state === "finished")
        $id("tournament-history-container").appendChild(container);
    else
        $id("tournament-current-games-container").appendChild(container);

}

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
    const gameCard = $id("tournament-game-" + gameObject.gameId);

    gameCard.querySelector(".tournament-game-card-spinner").style.display = "none";

    if (gameObject.state === "ongoing")
        gameCard.querySelector(".tournament-game-card-score").textContent = "0 - 0";
    else if (gameObject.state === "paused")
        gameCard.querySelector(".tournament-game-card-spinner").style.display = "flex";
    else if (gameObject.state === "finished") {
        console.log("FINIIIIISHH HIIIIIIIM!!!!!");
        //TODO: the winner value should be player1/2 instead of player id
        moveGameCardToHistory(gameObject.gameId);
    }
}

function createRankCard(rankCardObject) {
    const template = $id("tournament-rank-row-template").content.cloneNode(true);


    const container = template.querySelector(".tournament-rank-row");
    template.querySelector(".tournament-rank-row-position").textContent = rankCardObject.rank;
    template.querySelector(".tournament-rank-row-avatar").src = rankCardObject.avatarUrl;
    template.querySelector(".tournament-rank-row-username").textContent = rankCardObject.username;
    template.querySelector(".tournament-rank-row-wins").textContent = rankCardObject.wonGames;
    template.querySelector(".tournament-rank-row-diff").textContent = rankCardObject.winPoints;
    template.querySelector(".tournament-rank-row-games").textContent = rankCardObject.playedGames;

    $id("tournament-rank-table").appendChild(container);
}

export function updateTournamentRank(rankObject) {

    $id("tournament-rank-list-cards-list").innerHTML = "";

    for (let element of rankObject)
        createRankCard(element);
}

// =================================================================================================
// =================================================================================================
// =================================================================================================
// =================================================================================================
// =================================================================================================
// =================================================================================================


export function createGameList(games) {
    console.log("Creating game list with data: ", games);
    for (let element of games) {
        createGameCard(element);
    }
}

export function updateParticipantsCard(userData) {

    console.log("user data:", userData);


    
    // TODO:    a) on "accepted" the keyword is data.userState and on the others is data.state
    //          b) in the "join" message the avatar and username needs to be included

    if (!$id("tournament-players-list-player" + userData.id))
        createPlayerCard(userData);
    if (userData.state === "accepted") {
        changePlayerCardToAccepted(userData.id);
    }
    else if (userData.state === "leave"){
        removePlayerCard(userData.id);
        tournamentData.playersIds.pop(userData.id);
    }
}

