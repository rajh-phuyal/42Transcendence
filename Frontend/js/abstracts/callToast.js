import { $id, $class, $on } from '../abstracts/dollars.js';
import { audioPlayer } from '../abstracts/audio.js';
import router from '../navigation/router.js'

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

    $class("toast-container")[0].appendChild(container);
    $on(container, "click", routeToConversation);
    return container;
}

function removeToast(event) {
    event.target.remove();
}

/* DEFAULT TOAST RELATED */
export default function $callToast(type, message, conversation = null) {
    let toast = $id(`${type}-toast`);
    let toastMsg = $id(`${type}-toast-message`);

    if (conversation.id != null) {
        if (!$id(`message-toast-${conversation.id}`))
            toast = createConversationToast(conversation);
        else
            toast = $id(`message-toast-${conversation.id}`);
        toastMsg = toast.querySelector(".message-toast-message");
        message = `${conversation.username}: ${message}`;
    }

    audioPlayer.playSound("toast");
    if (!message)
        return ;
    toastMsg.textContent = message;
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 10000 }).show();

    // remove the conversation toast after it closes
    if (conversation.id != null) {
        toast.addEventListener('hidden.bs.toast', removeToast);
    }
}