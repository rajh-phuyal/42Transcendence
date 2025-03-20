import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';
import { tournamentData } from "./objects.js";

/* API CALLS */
export function joinTournament() {
    call(`tournament/join/${tournamentData.all.tournamentInfo.id}/`, 'PUT').then(data => {
        tournamentData.all.clientRole = "member";
        $callToast("success", data.message);
        console.log("ROLE:", tournamentData.all.clientRole);

    })
}

export function leaveTournament() {
    call(`tournament/leave/${tournamentData.all.tournamentInfo.id}/`, 'DELETE').then(data => {
        tournamentData.all.clientRole = "fan";
        $callToast("success", data.message);
        console.log("ROLE:", tournamentData.all.clientRole);
    });
}

export function startTournament() {
    call(`tournament/start/${tournamentData.all.tournamentInfo.id}/`, 'PUT').then(data => {
        $callToast("success", data.message);
    })
}

export function deleteTournament() {
    call(`tournament/delete/${tournamentData.all.tournamentInfo.id}/`, 'DELETE').then(data => {
        $callToast("success", data.message);
        router('/home');
    });
}