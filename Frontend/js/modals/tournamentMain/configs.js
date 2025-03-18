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

import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        tournamentId: undefined,
    },

    methods: {
        updateModalView() {
            /*
            This function shows / hides the buttons
            depending on if the client is already enrolled in a tournament
                enrolled:       show history & lobby buttons
                not enrolled:   show history,create & join buttons
            This function also updates the title
            */
           console.log("updateModalView");
           console.log(this.tournamentId);
            if(this.tournamentId){
                // Enrolled
                this.domManip.$id("modal-tournament-main-title").textContent = translate("tournamentMain", "title-enrolled");
                this.domManip.$id("modal-tournament-main-btn-create").style.display = "none";
                this.domManip.$id("modal-tournament-main-btn-join").style.display = "none";
                this.domManip.$id("modal-tournament-main-btn-history").style.display = "block";
                const btnLobby = this.domManip.$id("modal-tournament-main-btn-lobby");
                btnLobby.style.display = "block";
                this.domManip.$on(btnLobby, "click", this.callBackLobby);
            } else{
                // Not enrolled
                this.domManip.$id("modal-tournament-main-title").textContent = translate("tournamentMain", "title-normal");
                this.domManip.$id("modal-tournament-main-btn-create").style.display = "block";
                this.domManip.$id("modal-tournament-main-btn-join").style.display = "block";
                this.domManip.$id("modal-tournament-main-btn-history").style.display = "block";
                this.domManip.$id("modal-tournament-main-btn-lobby").style.display = "none";
           }
        },

        callBackLobby() {
            // Redirect to the lobby
            router(`/tournament`, { id: this.tournamentId });
        }
    },

    hooks: {
        beforeOpen () {
            // Check if client is already enrolled in a tournament
            call('tournament/enrolment/','GET').then(data => {
                console.log("enrolement:", data);
                this.tournamentId = data.tournamentId
                this.updateModalView();
            }).catch((error) => {
                console.log(error);
                router('/404');
            })
        },

        afterClose () {
        }
    }
}