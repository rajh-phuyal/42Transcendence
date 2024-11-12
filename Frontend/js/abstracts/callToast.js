import { $id } from '../abstracts/dollars.js';

export default function $callToast(type, message) {
    console.log("type", type);
    console.log("message", message);
    const toast = $id(`${type}-toast`);
    const toastMsg = $id(`${type}-toast-message`);
    
    if (message) {
        toastMsg.textContent = message;
        new bootstrap.Toast(toast, { autohide: true, delay: 10000 }).show();
        return ;
    }
    if (type == "success")
        message = 'Sucess!!';
    if (type == "error")
        message = 'Error!!';
}