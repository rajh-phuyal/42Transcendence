import { joinTournament, leaveTournament } from "./methodsApi.js";
import { changeTabs } from "./methodsView.js";

export function callbackTabButton(event) {
    changeTabs(event.srcElement.getAttribute("tab"));
}

export function callbackSubscribe(event) {
    joinTournament();
}

export function callbackUnsubscribe(event) {
    leaveTournament();
}


function callbackRankButton(event) {
    console.warn(event);
    this.changeTabs(event.srcElement.getAttribute("tab"));
}