import { $id, $class } from '../abstracts/dollars.js';
import { audioPlayer } from '../abstracts/audio.js';

function createConversationToast(conversationId) {
    const template = $id("message-toast-template").content.cloneNode(true);
    const container = template.querySelector(".message-toast");
    const toastId = `$message-toast-${conversationId}`;

    container.setAttribute("id", toastId);

    $class("toast-container").appendChild(container);
    return container;
}


export default function $callToast(type, message, conversationId = null) {
    console.warn("call toast entered")
    let toast = $id(`${type}-toast`);
    let toastMsg = $id(`${type}-toast-message`);

    if (conversationId != null) {
        if (!$id(`${type}-toast-${conversationId}`))
            toast = createConversationToast(conversationId);
        else
            toast = `$message-toast-${conversationId}`;
        toastMsg = toast.querySelector(".message-toast-message");
    }

    audioPlayer.playSound("toast");
    if (!message)
        return ;
    toastMsg.textContent = message;
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 10000 }).show();

    // remove the conversation toast after it closes
    if (conversationId != null) {
        toast.addEventListener('hidden.bs.toast', function () {
            toast.remove();
        });
    }
}