import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData } from "./objects.js";
import router from "../../navigation/router.js";
import { updateMembers } from "./methodsMembers.js";
import { callbackSubscribe, callbackUnsubscribe } from "./callbacks.js";

/* This function should be called when routing to lobby it will create for
    all tabs all elements. The elements can than during the tournament be updated
    by updateView function
*/
export function initView() {

/*
    if (data.tournamentInfo.state === "setup") {
        for (let element of data.tournamentMembers)
            createPlayerCard(element);
        this.changeTabs("participants");
    } */
    // TODO: uncomment this
    /* else {
        if (data.tournamentMembers.length == 3)
            updatePodium(data.tournamentMembers.find(member => member.rank === 3), "third", false);
        for (let element of data.tournamentGames) {
            createGameCard(element);
            updateFinalsDiagram(element);
        }
    }

    if (data.tournamentInfo.state !== "setup")
        updateRankTable(data.tournamentMembers);

*/


}

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
export function updateView() {
    // set tournament details
    const nameElement = $id("tournament-name");
    console.warn("tournamentData:", tournamentData);
    nameElement.innerText = tournamentData.all.tournamentInfo.name;
    updateIcons();
    updateMembers();
    // updateGames();// TODO:
    // updateRoundRobin();// TODO:
    // updateFinals();// TODO:
    updateButtons();

    // TODO: make this smarter
    changeTabs("members");
    // open the correct tab:
    // state setup:      users
    // state ongoing:    games//upcoming
    // state finished:   rank
    // hide / show the correct buttons:
    // state setup:
        // role: admin   start, delete
        // role: user    subscribe, unsubscribe
    // state ongoing / finished:
        // hide all buttons

  /*   console.log("state:", tournamentState);

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
        //$id("tournament-middle-bottom-current-game-button").style.display = "none";
        //$id("tournament-games-do-come-button").style.display = "none";
        //$id("button-subscribe-start").style.display = "none";
        //$id("button-unsubscribe-cancel").style.display = "none";
        //$id("tournament-current-games-container").style.display = "none";
        //$id("tournament-rank-container").style.display = "flex";
        //$id("tournament-history-container").style.display = "none";
        return ;

    }

    $id("tournament-rank-container").style.display = "none";
    $id("tournament-history-container").style.display = "none";*/
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
    // Hide all tabs
    $id("container-members").style.display          = "none";
    $id("container-finals").style.display           = "none";
    $id("container-round-robin").style.display      = "none";
    $id("container-games-upcoming").style.display   = "none";
    $id("container-games-finished").style.display   = "none";
    // Show the selected tab
    container.style.display = "flex";
    console.log("change to tab %s by showing %s", tab, container.getAttribute("id"));
}

/* This fucntion updates the tournament icons to the values stored in tournamentData.all */
function updateIcons() {
    const iconState     = $id("tournament-state-img");
    const iconPrivacy   = $id("tournament-privacy-img");
    const iconType      = $id("tournament-type-img");
    /* STATE */
    if (tournamentData.all.tournamentInfo.state === "setup")
        iconState.src = "../assets/icons_128x128/icon_tournament_state_setup.png";
    else if (tournamentData.all.tournamentInfo.state === "ongoing")
        iconState.src = "../assets/icons_128x128/icon_tournament_state_ongoing.png";
    else
        iconState.src = "../assets/icons_128x128/icon_tournament_state_finished.png";
    /* PRIVACY */
    if (tournamentData.all.tournamentInfo.public)
        iconPrivacy.src = "../assets/icons_128x128/icon_tournament_public.png";
    else
        iconPrivacy.src = "../assets/icons_128x128/icon_tournament_private.png";
    /* TYPE */
    if (tournamentData.all.tournamentInfo.local)
        iconType.src = "../assets/icons_128x128/icon_tournament_local.png";
    else
        iconType.src = "../assets/icons_128x128/icon_tournament_remote.png";
}

function updateButtons() {
    // Subscribe / Unsubscribe Button
    const buttonSubscribe = $id("button-subscribe");
    buttonSubscribe.style.display = "none"; // Hide by default
    buttonSubscribe.removeEventListener("click", callbackSubscribe);
    buttonSubscribe.removeEventListener("click", callbackUnsubscribe);
    console.log("ROLE:", tournamentData.all.clientRole);
    if (tournamentData.all.clientRole === "member") {
        buttonSubscribe.style.display = "block";
        buttonSubscribe.innerText = "Unsubscribe"; // TODO: translate
        buttonSubscribe.addEventListener("click", callbackUnsubscribe);
    } else if (tournamentData.all.clientRole === "invited") {
        buttonSubscribe.style.display = "block";
        buttonSubscribe.innerText = "Subscribe";  // TODO: translate
        buttonSubscribe.addEventListener("click", callbackSubscribe);
    } else if (tournamentData.all.clientRole === "fan" && tournamentData.all.tournamentInfo.public) {
        buttonSubscribe.style.display = "block";
        buttonSubscribe.innerText = "Subscribe";  // TODO: translate
        buttonSubscribe.addEventListener("click", callbackSubscribe);
    }
}