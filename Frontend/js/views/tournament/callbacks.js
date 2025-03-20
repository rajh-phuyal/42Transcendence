import { joinTournament, leaveTournament, startTournament } from "./methodsApi.js";
import { changeTabs } from "./methodsView.js";

export function callbackTabButton(event) {
    changeTabs(event.srcElement.getAttribute("tab"));
}


function callbackRankButton(event) {
    console.warn(event);
    this.changeTabs(event.srcElement.getAttribute("tab"));
}