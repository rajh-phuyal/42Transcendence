import { changeTabs } from "./methodsView.js";

export function callbackTabButton(event) {
    changeTabs(event.srcElement.getAttribute("tab"));
}
