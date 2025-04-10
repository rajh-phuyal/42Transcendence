import { $id } from '../../abstracts/dollars.js';
import router from '../../navigation/router.js';
import { modalManager } from '../../abstracts/ModalManager.js';

export function AIModalCallback(){
    // Set the opponent to AI
    const view = $id("router-view");
    view.setAttribute("data-user-id", "2");
    view.setAttribute("data-user-username", "ai");                                     // FUTURE: maybe this should be saved somewhere else as a constant
    view.setAttribute("data-user-avatar", "670eb5bf-72cb-45bc-b17c-9fcf029b9197.png"); // FUTURE: maybe this should be saved somewhere else as a constant
    modalManager.openModal("modal-create-game");
}

export function LocalModalCallback(){
    // Set the opponent to AI
    const view = $id("router-view");
    view.setAttribute("data-user-id", "3");
    view.setAttribute("data-user-username", "theThing");                               // FUTURE: maybe this should be saved somewhere else as a constant
    view.setAttribute("data-user-avatar", "4ca810c2-9b38-4bc8-ab87-d478cb1739f0.png"); // FUTURE: maybe this should be saved somewhere else as a constant
    modalManager.openModal("modal-create-game");
}

export function battleModalCallback(){
    // Remove the attributes from the view so that the user can select a friend in the modal
    const view = $id("router-view");
    view.removeAttribute("data-user-id");
    view.removeAttribute("data-user-username");
    view.removeAttribute("data-user-avatar");
    modalManager.openModal("modal-create-game");
}

export function tournamentModalCallback(){
    modalManager.openModal("modal-tournament-main");
}

export function chatRoomModalCallback(){
    router("/chat");
}