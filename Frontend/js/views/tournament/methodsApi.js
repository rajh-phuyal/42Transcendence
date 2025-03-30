import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import $callToast from '../../abstracts/callToast.js';
import { $id } from '../../abstracts/dollars.js';
import { tournamentData as data } from "./objects.js";
import { modalManager } from '../../abstracts/ModalManager.js';

export function joinTournament() {
    console.warn(data.tournamentInfo.local);
    // Let the modal decide if we need an approval
    const view = $id("router-view");
    view.setAttribute("data-tournament-id",             data.tournamentInfo.id);
    view.setAttribute("data-tournament-state",          data.tournamentInfo.state);
    view.setAttribute("data-tournament-local",          data.tournamentInfo.local);
    view.setAttribute("data-tournament-client-role",    data.clientRole);
    modalManager.openModal("modal-tournament-local-join");
}

export function leaveTournament() {
    call(`tournament/leave/${data.tournamentInfo.id}/`, 'DELETE').then(data => {
        $callToast("success", data.message);
    });
}

export function startTournament() {
    call(`tournament/start/${data.tournamentInfo.id}/`, 'PUT').then(data => {
        $callToast("success", data.message);
    })
}

export function deleteTournament() {
    call(`tournament/delete/${data.tournamentInfo.id}/`, 'DELETE').then(data => {
        $callToast("success", data.message);
        router('/home');
    });
}