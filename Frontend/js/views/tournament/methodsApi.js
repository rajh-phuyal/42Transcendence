import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';
import { tournamentData as data } from "./objects.js";

export function joinTournament() {
    call(`tournament/join/${data.tournamentInfo.id}/`, 'PUT').then(data => {
        $callToast("success", data.message);
    })
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