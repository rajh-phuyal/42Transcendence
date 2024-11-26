import $store from '../../store/store.js'

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
    const messageDiv = document.createElement('div');

    if (element.userId != $store.fromState("user").id) {
        const username = document.createElement('span');
        username.className = "chat-view-messages-message-sender";
        username.textContent = element.username;
        messageDiv.appendChild(username)
        messageDiv.className = "chat-view-incoming-message-container";
    }
    else
        messageDiv.className = "chat-view-sent-message-container";

    const messageBox = document.createElement('div');
    messageBox.className = "chat-view-messages-message-box";
    messageBox.textContent = element.content;
    messageDiv.appendChild(messageBox)

    const timeStamp = document.createElement('span');
    timeStamp.className = "chat-view-messages-message-time-stamp";
    timeStamp.textContent = formatTimestamp(element.createdAt);
    messageDiv.appendChild(timeStamp)

    return (messageDiv);
}