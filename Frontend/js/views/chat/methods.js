import $store from '../../store/store.js';
import { $id } from '../../abstracts/dollars.js'

export function createMessage(element) {

    let elementId = "chat-view-sent-message-template";
    if (element.userId != $store.fromState("user").id)
        elementId = "chat-view-incoming-message-template";

    let template = $id(elementId).content.cloneNode(true);

    if (element.userId != $store.fromState("user").id) 
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;

    template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    template.querySelector(".chat-view-messages-message-time-stamp").textContent = moment(element.createdAt).format("h:mma DD-MM-YYYY");
    return (template);
}