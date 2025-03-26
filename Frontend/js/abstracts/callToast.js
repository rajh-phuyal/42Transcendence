import { $id, $class, $on } from '../abstracts/dollars.js';
import { audioPlayer } from '../abstracts/audio.js';
import router from '../navigation/router.js'
import { translate } from '../locale/locale.js';
import { parseChatMessage } from '../views/chat/methods.js';

/* INTERNAL CHAT TOAST RELATED */
function routeToConversation(event) {
    if (event.target.getAttribute("type") === "button")
        return ;

    let toastContainer;
    let conversationId;

    toastContainer = event.target;

    for (let i = 0; i <= 2; i++) {
        conversationId = toastContainer.getAttribute("conversationId");
        if (conversationId)
            break
        toastContainer = toastContainer.parentNode;
    }

    const toastInstance = bootstrap.Toast.getInstance(toastContainer);
    if (toastInstance)
        toastInstance.hide();
    else
        console.warn("no toast instance");

    router('/chat', { id: conversationId });
}

function createConversationToast(conversation) {
    const template = $id("message-toast-template").content.cloneNode(true);
    const container = template.querySelector(".message-toast");
    const toastId = `message-toast-${conversation.id}`;

    container.setAttribute("conversationId", conversation.id);
    container.setAttribute("id", toastId);

    container.querySelector(".message-toast-avatar").src = `${window.origin}/media/avatars/${conversation.avatar}`;

    $class("toast-container-right")[0].appendChild(container);
    $on(container, "click", routeToConversation);
    return container;
}

function removeToast(event) {
    event.target.remove();
}

/* DEFAULT TOAST RELATED */
export default function $callToast(type, message, conversation = null) {
    let toastElement = "";
    let toastMsgElement = "";
    let toastTitle = "";
    let duration = "";
    if (conversation) {
        /* CHAT MESSAGE TOAST */
        duration = 20000
        if (!$id(`message-toast-${conversation.id}`)) {
            toastElement = createConversationToast(conversation);
            audioPlayer.playSound("chatToast");
        } else
        toastElement = $id(`message-toast-${conversation.id}`);
        toastMsgElement = toastElement.querySelector(".message-toast-message");
        message = parseChatMessage(message);
        toastTitle = translate("global:toast", "titleChat") + conversation.username;
    } else {
        /* SUCCESS / ERROR TOAST */
        duration = 5000
        if(!message)
            return;
        toastElement = $id(`${type}-toast`);
        toastMsgElement = $id(`${type}-toast-message`);
        toastTitle = translate("global:toast", "title");
        audioPlayer.playSound("toast");
        if  (type === "error")
            toastElement.classList.add("toast-error");
        else if (type === "success")
            toastElement.classList.add("toast-success");

    }
    let toastTitleElement = ""
    toastTitleElement = toastElement.querySelector(".toast-title");
    toastTitleElement.textContent = toastTitle;
    toastMsgElement.innerHTML = message;
    // Set duration
    // Create a new toast instance
    new bootstrap.Toast(toastElement, { autohide: true, delay: duration }).show();
    // remove the conversation toast after it closes
    if (conversation != null) {
        toastElement.addEventListener('hidden.bs.toast', removeToast);
    }
}