import { $id } from '../abstracts/dollars.js';
import { audioPlayer } from '../abstracts/audio.js';

export default function $callToast(type, message) {
    const toast = $id(`${type}-toast`);
    const toastMsg = $id(`${type}-toast-message`);
    audioPlayer.playSound("toast");
    if (message) {
        toastMsg.textContent = message;
        new bootstrap.Toast(toast, { autohide: true, delay: 10000 }).show();
        return ;
    }
    // TODO: what is this for? still needed?
    if (type == "success")
        message = 'Sucess!!';
    if (type == "error")
        message = 'Error!!';
}