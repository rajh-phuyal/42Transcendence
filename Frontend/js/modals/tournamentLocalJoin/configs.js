import { modalManager } from '../../abstracts/ModalManager.js';
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';

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
                $callToast("success", data.message);
                modalManager.closeModal("modal-tournament-local-join");
            })
        },
    },

    hooks: {
        async allowedToOpen() {
            let tournamentId            = this.domManip.$id("router-view").getAttribute("data-tournament-id");
            let tournamentState         = this.domManip.$id("router-view").getAttribute("data-tournament-state");
            let tournamentClientRole    = this.domManip.$id("router-view").getAttribute("data-tournament-client-role");
            let tournamentLocal         = this.domManip.$id("router-view").getAttribute("data-tournament-local");
            console.log("tournamentLocalJoin: allowedToOpen: ", tournamentId, tournamentState, tournamentClientRole, tournamentLocal);
            if(!tournamentId || !tournamentState || !tournamentClientRole) {
                console.error("tournamentLocalJoin: allowedToOpen: tournamentId, tournamentState or tournamentClientRole is not defined");
                return false;
            }

            if (tournamentState !== "setup")
                return false;
            if (tournamentClientRole === "fan" || tournamentClientRole === "invited") {
                if (tournamentLocal == "true")
                    return true;
                else {
                    this.joinTournament(tournamentId);
                    return false;
                }
            }
            return false
        },

        beforeOpen () {
            this.domManip.$on(this.domManip.$id("modal-tournament-local-join-btn-join"), "click", this.buttonCallback);
        },

        afterClose () {
            this.domManip.$off(this.domManip.$id("modal-tournament-local-join-btn-join"), "click", this.buttonCallback);
        }
    }
}