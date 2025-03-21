/* TODO: This file and it's logic is not revised yet */

import { $id } from "../../abstracts/dollars.js";
import router from "../../navigation/router.js";

export function updatePodium(member, position, show = true) {
    const podiumContainer = $id(`tournament-podium-${position}`);
    if(!podiumContainer || !member)
        return ;
    podiumContainer.querySelector(".tournament-podium-avatar").src = window.origin + "/media/avatars/" + member.avatar;
    podiumContainer.querySelector(".tournament-podium-username").textContent = member.username;
    podiumContainer.setAttribute("userid", member.id);
    if (show) {
        podiumContainer.querySelector(".tournament-podium-avatar").style.display = "flex";
        podiumContainer.querySelector(".tournament-podium-username").style.display = "flex";
        podiumContainer.querySelector(".tournament-podium-question-mark").style.display = "none";
    }
    // Add event listener to the podium
    podiumContainer.addEventListener("click", podiumCallback);
}

export function showThirdPlaceFinalsDiagram() {
    // Flex the podium for third place in case it already exists. this is here for games without semi-finals
    if ($id("tournament-podium-third").querySelector(".tournament-podium-username").textContent !== "") {
        $id("tournament-podium-third").querySelector(".tournament-podium-avatar").style.display = "flex";
        $id("tournament-podium-third").querySelector(".tournament-podium-username").style.display = "flex";
        $id("tournament-podium-third").querySelector(".tournament-podium-question-mark").style.display = "none";
    }
}

export function updateFinalsDiagram(game) {
    if (game.type === "normal")
        return ;
    // This is for the final games wich come without the players first
    if (!game.playerLeft || !game.playerRight)
        return ;

    let diagramContainer = $id(`tournament-${game.type}-${game.id}`);

    if (!diagramContainer) {
        const template = $id("tournament-finals-template").content.cloneNode(true);
        diagramContainer = template.querySelector(".tournament-finals-diagram-container");
        diagramContainer.setAttribute("id", `tournament-${game.type}-${game.id}`);
        diagramContainer.setAttribute("gameid", game.id);
        diagramContainer.addEventListener("click", gameFinalsCallback);
        $id("tournment-finals-diagram").prepend(diagramContainer);
    }

    diagramContainer.querySelector(".finals-title").textContent = game.type;
    diagramContainer.querySelector(".finals-player-left-username").textContent = game.playerLeft.username;
    diagramContainer.querySelector(".finals-player-right-username").textContent = game.playerRight.username;
    diagramContainer.querySelector(".finals-player-left-avatar").src = window.origin + "/media/avatars/" + game.playerLeft.avatar;
    diagramContainer.querySelector(".finals-player-right-avatar").src = window.origin + "/media/avatars/" + game.playerRight.avatar;

    if (game.state !== "pending") {
        diagramContainer.querySelector(".finals-score").textContent = game.playerLeft.points + "-" + game.playerRight.points;
    }

    if (!(game.state === "finished" || game.state === "quited"))
        return;
    if (game.playerLeft.result === "won") {
        diagramContainer.querySelector(".finals-player-right-avatar").style.filter = "brightness(50%)";
        diagramContainer.querySelector(".finals-player-right-username").style.filter = "brightness(50%)";
        if (game.type === "final") {
            updatePodium(game.playerLeft, "first");
            updatePodium(game.playerRight, "second");
            showThirdPlaceFinalsDiagram();
        }
        if (game.type === "thirdplace") {
            updatePodium(game.playerLeft, "third");
        }
    }
    else {
        diagramContainer.querySelector(".finals-player-left-avatar").style.filter = "brightness(50%)";
        diagramContainer.querySelector(".finals-player-left-username").style.filter = "brightness(50%)";
        if (game.type === "final") {
            updatePodium(game.playerLeft, "second");
            updatePodium(game.playerRight, "first");
            showThirdPlaceFinalsDiagram();
        }
        if (game.type === "thirdplace") {
            updatePodium(game.playerRight, "third");
        }
    }
}

function gameFinalsCallback(event) {
    const gameId = event.currentTarget.getAttribute("gameid");
    router(`/game`, { id: gameId });
}

function podiumCallback(event) {
    const userId = event.currentTarget.getAttribute("userid");
    router(`/profile`, { id: userId });
}