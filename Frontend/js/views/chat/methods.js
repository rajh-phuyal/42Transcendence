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

    // let cenas = document.querySelector(elementId);
    // console.log("cenas",cenas);
    let template = $id(elementId).content.cloneNode(true);

    // const messageDiv = document.createElement('div');   

    if (element.userId != $store.fromState("user").id) {
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;

        // const username = document.createElement('span');
        // username.className = "chat-view-messages-message-sender";
        // username.textContent = element.username;
        // messageDiv.appendChild(username)
        // messageDiv.className = "chat-view-incoming-message-container";
    }
    // else{
    //     template = document.getElementById("chat-view-sent-message-template");//.content.cloneNode(true);
    //     console.log("template", template);
    //     return;
    //     messageDiv = template.querySelector(".chat-view-sent-message-container");
    //     // messageDiv.className = "chat-view-sent-message-container";
    // }


    template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    // const messageBox = document.createElement('div');
    // messageBox.className = "chat-view-messages-message-box";
    // messageBox.textContent = element.content;
    // messageDiv.appendChild(messageBox);

    template.querySelector(".chat-view-messages-message-time-stamp").textContent = formatTimestamp(element.createdAt);
    // const timeStamp = document.createElement('span');
    // timeStamp.className = "chat-view-messages-message-time-stamp";
    // timeStamp.textContent = formatTimestamp(element.createdAt);
    // messageDiv.appendChild(timeStamp)

    return (template);
}