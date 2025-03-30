import { $id, $addClass } from '../../abstracts/dollars.js'

export function showTypingIndicator(endTimestamp) {
    const container = $id("chat-view-messages-container");
    let typingElement = $id("chat-view-message-container-typing");

    // If the typing box is already there, update the timestamp and return
    if (typingElement) {
        typingElement.setAttribute("data-endtime", endTimestamp);
        return;
    }

    // Clone the message template
    let template = $id("chat-view-message-template").content.cloneNode(true);

    // Set up the typing indicator
    let messageContainer = template.querySelector(".chat-view-message-container");
    $addClass(messageContainer, "chat-view-message-container-incoming");
    $addClass(messageContainer, "chat-view-message-container-typing");
    messageContainer.id = "chat-view-message-container-typing";
    messageContainer.setAttribute("data-endtime", endTimestamp);

    // Set the box content to display animated dots
    let messageBox = template.querySelector(".chat-view-message-box");
    messageBox.textContent = ".";

    // Set timestamp to " " (so that the box has a border)
    let timestampElement = template.querySelector(".chat-view-message-timestamp");
    timestampElement.textContent = " ";

    // Append to container
    const lastChild = container.lastElementChild;
    if (!lastChild || !lastChild.classList.contains("chat-view-help-message-container"))
        container.appendChild(template);
    else
        // If the help message is already there, we need to insert the type indicator before it
        container.insertBefore(template, lastChild);

    // Scroll to the bottom
    let scrollContainer = $id("chat-view-messages-container");
    scrollContainer.scrollTop = scrollContainer.scrollHeight + scrollContainer.clientHeight;

    // Start the dot animation and removal timer
    animateTypingIndicator();
}

function animateTypingIndicator() {
    let typingElement = $id("chat-view-message-container-typing");
    if (!typingElement)
        return;

    let messageBox = typingElement.querySelector(".chat-view-message-box");
    if (!messageBox)
        return;

    let interval = setInterval(() => {
        let endTimestamp = parseInt(typingElement.getAttribute("data-endtime"), 10);

        // If time over, remove the typing indicator
        if (Date.now() > endTimestamp) {
            typingElement.remove();
            clearInterval(interval);
            return;
        }

        // Upate the dots . -> .. -> ... -> .
        if (messageBox.textContent.length < 3)
            messageBox.textContent += ".";
        else
            messageBox.textContent = ".";
    }, 500);
}
