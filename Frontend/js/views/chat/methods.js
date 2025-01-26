import $store from '../../store/store.js';
import { $id } from '../../abstracts/dollars.js'

export function createMessage(element, prepend = true, adjustScroll = true) {
    const container = $id("chat-view-messages-container");

    // If adjusting scroll, calculate the scroll position before adding the message
    let previousScrollHeight = 0;
    let previousScrollTop = 0;
    if (adjustScroll) {
        previousScrollHeight = container.scrollHeight;
        previousScrollTop = container.scrollTop;
    }

    // Determine the correct template for the message
    let elementId = "chat-view-sent-message-template";
    if (element.username == "overlords")
        elementId = "chat-view-overlords-message-template";
    else if (element.userId != $store.fromState("user").id)
        elementId = "chat-view-incoming-message-template";

    let template = $id(elementId).content.cloneNode(true);

    if (element.userId != $store.fromState("user").id)
        template.querySelector(".chat-view-messages-message-sender").textContent = element.username;

    if (element.userId == 1)
        template.querySelector(".chat-view-messages-message-overlords-box").textContent = element.content;
    else
        template.querySelector(".chat-view-messages-message-box").textContent = element.content;
    template.querySelector(".chat-view-messages-message-time-stamp").textContent = moment(element.createdAt).format("h:mma DD-MM-YYYY");

    // Prepend or append the message to the container
    if (prepend) {
        container.prepend(template);
    } else {
        container.appendChild(template);
    }

    // If adjusting scroll, restore the user's scroll position
    if (adjustScroll) {
        const newScrollHeight = container.scrollHeight;
        container.scrollTop = previousScrollTop + (newScrollHeight - previousScrollHeight);
    }
    //return (template);
}