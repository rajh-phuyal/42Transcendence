import $store from '../../store/store.js';
import { $id } from '../../abstracts/dollars.js'

export function createMessage(element) {

    console.log("message json:", element);

    let elementId = "chat-view-sent-message-template";
    if (element.username == "overlords")
        elementId = "chat-view-overlords-message-template";
    else if (element.userId != $store.fromState("user").id)
        elementId = "chat-view-incoming-message-template";

    console.log("element id:",elementId);
    let template = $id(elementId).content.cloneNode(true);
    
    if (element.userId != $store.fromState("user").id) 
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;
    
    if (element.userId == 1)
        template.querySelector(".chat-view-messages-message-overlords-box").textContent = element.content;
    else
        template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    template.querySelector(".chat-view-messages-message-time-stamp").textContent = moment(element.createdAt).format("h:mma DD-MM-YYYY");
    return (template);
}