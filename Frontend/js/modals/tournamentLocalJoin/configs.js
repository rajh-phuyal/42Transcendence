/*
TODO: THIS MODAL IS NOT DONE AT ALL!!!
    NEED TO:
        - copy the right structure from the template modal
        - double check all nodes/elements if needed?
        - adjust the js code
            - move it from original configs.js (profile/home) to congigs.js of modal!
            - make sure the js code has all values. the idea is that the view stores the info as attribute and the modal takes it from there
            - e.g. newConversation modal js!
*/

import { modalManager } from '../../abstracts/ModalManager.js';
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';

export default {
    attributes: {

    },

    methods: {
        buttonCallback() {
            let tournamentId = this.domManip.$id("router-view").getAttribute("data-tournament-id");
            this.joinTournament(tournamentId);
        },

        joinTournament(tournamentId) {
            call(`tournament/join/${tournamentId}/`, 'PUT').then(data => {
                console.log(data);
                $callToast("success", data.message);
                modalManager.closeModal("modal-tournament-local-join");
            })
        },

        startTournament(tournamentId) {
            call(`tournament/start/${tournamentId}/`, 'PUT').then(data => {
                console.log(data);
                $callToast("success", data.message);
            })
        },
    },

    hooks: {
        async allowedToOpen() {
            let tournamentId            = this.domManip.$id("router-view").getAttribute("data-tournament-id");
            let tournamentState         = this.domManip.$id("router-view").getAttribute("data-tournament-state");
            let tournamentClientRole    = this.domManip.$id("router-view").getAttribute("data-tournament-client-role");
            let tournamentLocal         = this.domManip.$id("router-view").getAttribute("data-tournament-local");
            console.log("tournamentLocalJoin: allowedToOpen: ", tournamentId, tournamentState, tournamentClientRole);
            if(!tournamentId || !tournamentState || !tournamentClientRole) {
                console.error("tournamentLocalJoin: allowedToOpen: tournamentId, tournamentState or tournamentClientRole is not defined");
                return false;
            }

            if (tournamentState !== "setup")
                return false;
            if (tournamentClientRole === "admin") {
                console.log("starting tournament");
                this.startTournament(tournamentId);
                return false;
            }
            else {
                if (tournamentLocal)
                    return true;
                this.joinTournament(tournamentId);
            }
        },

        beforeOpen () {
            this.domManip.$on(this.domManip.$id("modal-tournament-local-join-btn-join"), "click", this.buttonCallback);
        },

        afterClose () {
            this.domManip.$off(this.domManip.$id("modal-tournament-local-join-btn-join"), "click", this.buttonCallback);
        }
    }
}