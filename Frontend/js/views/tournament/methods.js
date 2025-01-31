import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData } from "./objects.js";


export function buildView(tournamentState) {

    console.log("state:", tournamentState);

    let flexDivs;
    let hideDivs;

    if (tournamentState === "setup") {
        flexDivs = $class("tournament-setup")
        hideDivs = $class("tournament-ongoing")
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
        console.log("noning:", element.getAttribute("id"));
        element.style.display = 'none';
    }

    $id("tournament-rank-container").style.display = "none"; 
    $id("tournament-history-container").style.display = "none"; 
}

export function createPlayerCard(playerObject) {

    console.log("player", playerObject);

    tournamentData.playersIds.push(playerObject.userId);

    const template = $id("tournament-players-list-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-players-list-player-card");

    container.setAttribute("id", "tournament-players-list-player" + playerObject.userId)

    if (playerObject.userAvatar)
        template.querySelector(".tournament-players-list-player-card-avatar").src = window.origin + "/media/avatars/" + playerObject.userAvatar;
    else
    template.querySelector(".tournament-players-list-player-card-avatar").style.display = "none";
    template.querySelector(".tournament-players-list-player-card-username").textContent = playerObject.username;

    if (playerObject.userState === "pending")
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

    container.setAttribute("id", "tournament-game-" + gameObject.gameId)
    template.querySelector(".tournament-game-card-player1-avatar").src = window.origin + "/media/avatars/" + gameObject.player1.avatarPath;
    template.querySelector(".tournament-game-card-player2-avatar").src = window.origin + "/media/avatars/" + gameObject.player2.avatarPath;
    template.querySelector(".tournament-game-card-player1-username").textContent = gameObject.player1.username;
    template.querySelector(".tournament-game-card-player2-username").textContent = gameObject.player2.username;

    if (gameObject.state === "pending")
        template.querySelector(".tournament-game-card-score").textContent = "VS";
    else
        template.querySelector(".tournament-game-card-score").textContent = gameObject.player1.points + "-" + gameObject.player2.points; 

    if (gameObject.state === "finished")
        $id("tournament-history-container").appendChild(container);
    else
        $id("tournament-current-games-container").appendChild(container);

}

export function moveGameCardToHistory(gameId) {
    $id("tournament-history-container").appendChild($id("tournament-game-" + gameId));
}

export function updateGameCardScore(gameObject) {
    $id("tournament-game-" + gameId).querySelector(".tournament-game-card-score").textContent = gameObject.player1.points + "-" + gameObject.player2.points; 
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
        $id("game-list").appendChild(createGameCard(element));
    }
}

// export function createGameCard(gameData) {
//     console.log("Creating game card with data: ", gameData);

//     // Clone the template
//     let template = $id("game-card-template").content.cloneNode(true);
//     const card = template.querySelector(".game-card");
//     card.setAttribute("game-id", gameData.userId);
//     // Update the card background color based on user state
//     if (gameData.state === "pending")
//         template.querySelector(".game-card").style.backgroundColor = "grey";
//     else if (gameData.state === "ongoing")
//         template.querySelector(".game-card").style.backgroundColor = "orange";
//     else if (gameData.state === "paused")
//         template.querySelector(".game-card").style.backgroundColor = "yelllow";
//     else if (gameData.state === "finished")
//         template.querySelector(".game-card").style.backgroundColor = "green";
//     else if (gameData.state === "quited")
//         template.querySelector(".game-card").style.backgroundColor = "red";

//     // Populate the template fields with user data
//     template.querySelector(".game-id .value").textContent = gameData.gameId;
//     template.querySelector(".map-number .value").textContent = gameData.mapNumber;
//     template.querySelector(".game-state .value").textContent = gameData.state;
//     template.querySelector(".finish-time .value").textContent = gameData.finishTime;
//     template.querySelector(".deadline .value").textContent = gameData.deadline;
//     template.querySelector(".avatar1 .value").textContent = gameData.player1.avatarPath;
//     template.querySelector(".username1 .value").textContent = gameData.player1.username;
//     template.querySelector(".points1 .value").textContent = gameData.player1.points1;
//     template.querySelector(".result1 .value").textContent = gameData.player1.result1;
//     template.querySelector(".avatar2 .value").textContent = gameData.player2.avatarPath;
//     template.querySelector(".username2 .value").textContent = gameData.player2.username;
//     template.querySelector(".points2 .value").textContent = gameData.player2.points;
//     template.querySelector(".result2 .value").textContent = gameData.player2.result;

//     // Return the populated card
//     return template;
// }

// export function createParticipantCard(userData) {
//     console.log("Creating participant card for user with data: ", userData);

//     // Clone the template
//     let template = $id("tournament-list-card-template").content.cloneNode(true);
//     const card = template.querySelector(".card");
//     card.setAttribute("user-id", userData.userId);
//     // Update the card background color based on user state
//     if (userData.userState === "pending") {
//         template.querySelector(".card").style.backgroundColor = "grey";
//     }

//     // Populate the template fields with user data
//     template.querySelector(".user-id .value").textContent = userData.userId;
//     template.querySelector(".username .value").textContent = "Username: " + userData.username;
//     template.querySelector(".user-avatar").src = "https://localhost/media/avatars/" + userData.userAvatar;
//     template.querySelector(".user-avatar").alt = `Avatar of ${userData.username}`;
//     template.querySelector(".user-state .value").textContent = "State: " + userData.userState;

//     // Return the populated card
//     return template;
// }

export function updateParticipantsCard(userData) {

    console.log("user data:", userData);

    
    // TODO:    a) on "accepted" the keyword is data.userState and on the others is data.state
    //          b) in the "join" message the avatar and username needs to be included


    if (userData.userState === "accepted") {
        changePlayerCardToAccepted(userData.userId);
    }
    else if (userData.state === "join")
        createPlayerCard(userData);
    else if (userData.state === "leave"){
        removePlayerCard(userData.userId);
        tournamentData.playersIds.pop(userData.userState);
    }

    console.log("incoming state:", userData.userState);
    console.log("expected state: leave");
    console.log("players:", tournamentData.playersIds);
}

