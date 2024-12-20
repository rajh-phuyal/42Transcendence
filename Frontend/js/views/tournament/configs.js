import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import { createParticipantCard } from './methods.js';

export default {
    attributes: {

    },

    methods: {
        buildParticipantsList(list) {
            //console.log("Building participants list from list: ", list);
            const mainDiv = this.domManip.$id("tournament-list");
            for (let element of list){
                //console.log("participant card:", particpantCard);
                mainDiv.appendChild(createParticipantCard(element));
            }
        },

        joinTournament() {
            console.log("Joining tournament");
            const id = 5;   // TODO: MAKE IT COME FROM THE URL
            call(`tournament/join/${id}/`, 'PUT').then(data => {
                console.log(data);
                $callToast("success", data.message);
            })
            this.domManip.$id("join-button").style.display = "none";
            this.domManip.$id("leave-button").style.display = "block";
        },

        leaveTournament() {
            console.log("Leaving tournament");
            const id = 5;   // TODO: MAKE IT COME FROM THE URL
            call(`tournament/leave/${id}/`, 'DELETE').then(data => {
                console.log(data);
                $callToast("success", data.message);
            })
            this.domManip.$id("leave-button").style.display = "none";
            this.domManip.$id("join-button").style.display = "block";
        },

        startTournament() {
            console.log("Starting tournament");
            const id = 5;   // TODO: MAKE IT COME FROM THE URL
            call(`tournament/start/${id}/`, 'PUT').then(data => {
                console.log(data);
                $callToast("success", data.message);
            })
        },

        cancelTournament() {
            console.log("Cancelling tournament");
            const id = 5;   // TODO: MAKE IT COME FROM THE URL
            call(`tournament/delete/${id}/`, 'DELETE').then(data => {
                console.log(data);
                $callToast("success", data.message);
            })
        }
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            this.domManip.$off(this.domManip.$id("join-button"), "click", this.joinTournament);
            this.domManip.$off(this.domManip.$id("leave-button"), "click", this.leaveTournament);
            this.domManip.$off(this.domManip.$id("start-button"), "click", this.startTournament);
            this.domManip.$off(this.domManip.$id("cancel-button"), "click", this.cancelTournament);
            WebSocketManager.setCurrentRoute(undefined);
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            WebSocketManager.setCurrentRoute("tournament");
            const id = 5;  // TODO: MAKE IT COME FROM THE URL
            call(`tournament/lobby/${id}/`, 'GET').then(data => {
                //console.log(data);
                let stateColor;
                if (data.tournamentState == "setup")
                    stateColor = "orange";
                else if (data.tournamentState == "ongoing")
                    stateColor = "green";
                else
                    stateColor = "red";
                this.domManip.$id("status").style.backgroundColor = stateColor;
                this.domManip.$id("status").textContent = "State: " + data.tournamentState;
                this.domManip.$id("tournament-name").textContent = "Tournament Name: " + data.tournamentName;
                this.domManip.$id("client-role").textContent = "Client Role: " + data.clientRole;

                this.buildParticipantsList(data.tournamentMembers);

                this.domManip.$on(this.domManip.$id("join-button"), "click", this.joinTournament);
                this.domManip.$on(this.domManip.$id("leave-button"), "click", this.leaveTournament);
                this.domManip.$on(this.domManip.$id("start-button"), "click", this.startTournament);
                this.domManip.$on(this.domManip.$id("cancel-button"), "click", this.cancelTournament);
                this.domManip.$id("leave-button").style.display = "none";
            })
        },
    }
}