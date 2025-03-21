import { changeTabs } from "./methodsView.js";

export function callbackTabButton(event) {
    changeTabs(event.srcElement.getAttribute("tab"));
    // Set key tab focus to somwhere else
    event.srcElement.blur();
}
