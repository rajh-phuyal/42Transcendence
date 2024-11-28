import $store from '../../store/store.js';
import { $id } from '../../abstracts/dollars.js'

function formatTimestamp(timestamp) {
    // Parse the timestamp into a Date object
    const date = new Date(timestamp);

    // Get hours, minutes, and AM/PM
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12 || 12;

    // Get day, month, and year
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const year = date.getFullYear();

    // Return formatted string
    return `${hours}:${minutes}${ampm} ${day}-${month}-${year}`;
}

export function createMessage(element) {

    let elementId = "chat-view-sent-message-template";
    if (element.userId != $store.fromState("user").id)
        elementId = "chat-view-incoming-message-template";

    let template = $id(elementId).content.cloneNode(true);

    if (element.userId != $store.fromState("user").id) 
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;

    template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    template.querySelector(".chat-view-messages-message-time-stamp").textContent = formatTimestamp(element.createdAt);
    return (template);
}