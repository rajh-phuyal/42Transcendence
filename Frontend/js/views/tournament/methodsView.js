import router from "../../navigation/router.js";
import { $id , $addClass, $removeClass, $class} from "../../abstracts/dollars.js";
import { translate } from '../../locale/locale.js';
import { tournamentData as data } from "./objects.js";
import { updateMembers } from "./methodsMembers.js";
import { updateGames } from "./methodsGames.js";
import { updateRoundRobin } from "./methodsRankTable.js";
import { deleteTournament, joinTournament, leaveTournament, startTournament } from "./methodsApi.js";

/* This fucntion should be the main function to update the view according to the data
    Threfore it should:
        - set tournament details
            - tournament name
            - icons (state, privacy, type)
        - open the correct tab:
            - state setup:      users
            - state ongoing:    games-upcoming
            - state finished:   rank
        - hide / show the correct buttons:
            - state setup:
                - role: admin   start, delete
                - role: user    subscribe, unsubscribe
            - state ongoing / finished:
                - hide all buttons
        */
export function updateView(isGame = false) {
    // If state is deleted, redirect to home
    if (data.tournamentInfo.state === "deleted") {
        router('/home');
        return ;
    }
    // set tournament details
    const nameElement = $id("tournament-name");
    nameElement.innerText = data.tournamentInfo.name;
    updateIcons();
    updateButtons();

    // Update the Member Cards
    updateMembers();
    // Update the Game Cards
    updateGames();
    // Update the Round Robin Table
    updateRoundRobin();
    // Open the correct tab
    if(data.tournamentInfo.state === "setup")
        changeTabs("members");
    else if(!isGame && data.tournamentInfo.state === "ongoing")
        changeTabs("games-upcoming");
    else if (!isGame && data.tournamentInfo.state === "finished")
        changeTabs("finals");
}

/* This function shows and hides the main div of the different tabs
    ALLOWED TABS ARE: members games-upcoming games-finished rank
*/
export function changeTabs(tab) {
    const container = $id("container-" + tab);
    if (!container) {
        console.warn("Tab not found:", tab);
        return;
    }
    // Update the toggle butons style
    $removeClass(   $id("button-tab-members"),         "modal-toggle-button-enabled");
    $addClass(      $id("button-tab-members"),         "modal-toggle-button-disabled");
    $removeClass(   $id("button-tab-finals"),          "modal-toggle-button-enabled");
    $addClass(      $id("button-tab-finals"),          "modal-toggle-button-disabled");
    $removeClass(   $id("button-tab-round-robin"),     "modal-toggle-button-enabled");
    $addClass(      $id("button-tab-round-robin"),     "modal-toggle-button-disabled");
    $removeClass(   $id("button-tab-games-upcoming"),  "modal-toggle-button-enabled");
    $addClass(      $id("button-tab-games-upcoming"),  "modal-toggle-button-disabled");
    $removeClass(   $id("button-tab-games-finished"),  "modal-toggle-button-enabled");
    $addClass(      $id("button-tab-games-finished"),  "modal-toggle-button-disabled");
    // Enable the selected tab
    $removeClass(   $id("button-tab-" + tab),          "modal-toggle-button-disabled");
    $addClass(      $id("button-tab-" + tab),          "modal-toggle-button-enabled");
    // Hide all tabs
    $id("container-members").style.display          = "none";
    $id("container-finals").style.display           = "none";
    $id("container-round-robin").style.display      = "none";
    $id("container-games-upcoming").style.display   = "none";
    $id("container-games-finished").style.display   = "none";
    // Show the selected tab
    container.style.display = "flex";
}

/* This fucntion updates the tournament icons to the values stored in tournamentData.all */
function updateIcons() {
    const iconState     = $id("tournament-state-img");
    const iconPrivacy   = $id("tournament-privacy-img");
    const iconType      = $id("tournament-type-img");
    /* STATE */
    if (data.tournamentInfo.state === "setup") {
        iconState.src = "../assets/icons_128x128/icon_tournament_state_setup.png";
        iconState.title = translate("tournament", "tooltipTournamentStateSetup");
    }
    else if (data.tournamentInfo.state === "ongoing") {
        iconState.src = "../assets/icons_128x128/icon_tournament_state_ongoing.png";
        iconState.title = translate("tournament", "tooltipTournamentStateOngoing");
    }
    else {
        iconState.src = "../assets/icons_128x128/icon_tournament_state_finished.png";
        iconState.title = translate("tournament", "tooltipTournamentStateFinished");
    }
    /* PRIVACY */
    if (data.tournamentInfo.public) {
        iconPrivacy.src = "../assets/icons_128x128/icon_tournament_public.png";
        iconPrivacy.title = translate("tournament", "tooltipTournamentPublic");
    }
    else {
        iconPrivacy.src = "../assets/icons_128x128/icon_tournament_private.png";
        iconPrivacy.title = translate("tournament", "tooltipTournamentPrivate");
    }
    /* TYPE */
    if (data.tournamentInfo.local) {
        iconType.src = "../assets/icons_128x128/icon_tournament_local.png";
        iconType.title = translate("tournament", "tooltipTournamentLocal");
    }
    else {
        iconType.src = "../assets/icons_128x128/icon_tournament_remote.png";
        iconType.title = translate("tournament", "tooltipTournamentRemote");
    }
}

function updateButtons() {
    // Tab Buttons
    const buttonMembers = $id("button-tab-members");
    const buttonFinals = $id("button-tab-finals");
    const buttonRoundRobin = $id("button-tab-round-robin");
    const buttonGamesFinished = $id("button-tab-games-finished");
    const buttonGamesUpcoming = $id("button-tab-games-upcoming");
    if(data.tournamentInfo.state === "setup") {
        buttonMembers.style.display         = "block";
        buttonFinals.style.display          = "none";
        buttonRoundRobin.style.display      = "none";
        buttonGamesFinished.style.display   = "none";
        buttonGamesUpcoming.style.display   = "none";
    } else if(data.tournamentInfo.state === "ongoing") {
        buttonMembers.style.display         = "block";
        buttonFinals.style.display          = "block";
        buttonRoundRobin.style.display      = "block";
        buttonGamesFinished.style.display   = "block";
        buttonGamesUpcoming.style.display   = "block";
    } else {
        buttonMembers.style.display         = "block";
        buttonFinals.style.display          = "block";
        buttonRoundRobin.style.display      = "block";
        buttonGamesFinished.style.display   = "block";
        buttonGamesUpcoming.style.display   = "none";
    }

    // Start & Delete Tournament Button
    const buttonStart = $id("button-start");
    buttonStart.style.display = "none"; // Hide by default
    buttonStart.removeEventListener("click", startTournament);
    const buttonDelete = $id("button-delete");
    buttonDelete.style.display = "none"; // Hide by default
    buttonDelete.removeEventListener("click", deleteTournament);
    if (data.clientRole === "admin" && data.tournamentInfo.state === "setup") {
        buttonStart.style.display = "block";
        buttonStart.addEventListener("click", startTournament);
        buttonDelete.style.display = "block";
        buttonDelete.addEventListener("click", deleteTournament);
    }
    // Subscribe / Unsubscribe Button
    const buttonSubscribe = $id("button-subscribe");
    buttonSubscribe.style.display = "none"; // Hide by default
    if (data.tournamentInfo.state === "setup") {
        buttonSubscribe.removeEventListener("click", joinTournament);
        buttonSubscribe.removeEventListener("click", leaveTournament);
        if (data.clientRole === "member") {
            buttonSubscribe.style.display = "block";
            buttonSubscribe.innerText = translate("tournament", "btnUnsubscribe");
            buttonSubscribe.addEventListener("click", leaveTournament);
        } else if (data.clientRole === "invited") {
            buttonSubscribe.style.display = "block";
            buttonSubscribe.innerText = translate("tournament", "btnSubscribe");
            buttonSubscribe.addEventListener("click", joinTournament);
        } else if (data.clientRole === "fan" && data.tournamentInfo.public) {
            buttonSubscribe.style.display = "block";
            buttonSubscribe.innerText = translate("tournament", "btnSubscribe");
            buttonSubscribe.addEventListener("click", joinTournament);
        }
    }
}