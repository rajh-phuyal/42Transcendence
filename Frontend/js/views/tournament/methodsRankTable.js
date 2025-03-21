import { $id } from "../../abstracts/dollars.js";
import { tournamentData as data } from "./objects.js";
import router from "../../navigation/router.js";

export function updateRoundRobin() {
    // Translate the table headers TODO:
    $id("tournament-rank-table-header-rank").textContent    = "TRANSLATE";
    $id("tournament-rank-table-header-player").textContent  = "TRANSLATE";
    $id("tournament-rank-table-header-wins").textContent    = "TRANSLATE";
    $id("tournament-rank-table-header-diff").textContent    = "TRANSLATE";
    $id("tournament-rank-table-header-games").textContent   = "TRANSLATE";
    // Delete all previous rows
    $id("tournament-rank-table-body").innerHTML = "";
    // Sort the members by rank
    const sortedMembers = data.tournamentMembers.sort((a, b) => a.rank - b.rank);
    // Create all rank table rows
    for (let member of sortedMembers) {
        createRankEntry(member);
    }
}

function createRankEntry(member) {
    const template = $id("tournament-rank-row-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-rank-row");
    // Store the user id
    container.setAttribute("userid", member.id)
    // Add event listener to the row
    container.addEventListener("click", rankRowCallback);
    // Fill the row with data
    container.querySelector(".tournament-rank-row-position").textContent = member.rank;
    container.querySelector(".tournament-rank-row-avatar").src = window.origin + "/media/avatars/" + member.avatar;
    container.querySelector(".tournament-rank-row-username").textContent = member.username;
    container.querySelector(".tournament-rank-row-wins").textContent = member.wonGames;
    container.querySelector(".tournament-rank-row-diff").textContent = member.winPoints;
    container.querySelector(".tournament-rank-row-games").textContent = member.playedGames;
    // Append the row
    $id("tournament-rank-table-body").appendChild(container);
}

function rankRowCallback(event) {
    const userId = event.currentTarget.getAttribute("userid");
    router(`/profile`, { id: userId });
}
