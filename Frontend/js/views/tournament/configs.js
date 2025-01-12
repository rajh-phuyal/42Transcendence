import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import router from '../../navigation/router.js';
// import { createParticipantCard } from './methods.js';
import { buildView, createPlayerCard } from './methods.js';


export default {
    attributes: {
        data: undefined,
    },

    methods: {

        openCurrentGames() {
            this.domManip.$id("tournament-current-games-container").style.display = "flex";
            this.domManip.$id("tournament-rank-container").style.display = "none";
            this.domManip.$id("tournament-history-container").style.display = "none";
        },

        openTournamentRank() {
            this.domManip.$id("tournament-current-games-container").style.display = "none";
            this.domManip.$id("tournament-rank-container").style.display = "flex";
            this.domManip.$id("tournament-history-container").style.display = "none";
        },

        openTournamentHistory() {
            this.domManip.$id("tournament-current-games-container").style.display = "none";
            this.domManip.$id("tournament-rank-container").style.display = "none";
            this.domManip.$id("tournament-history-container").style.display = "flex";
        },

        quitCancelTournamentButtonAction() {
            if (this.data.tournamentState !== "setup")
                return
            if (this.data.clientRole === "admin") {
                console.log("canceling tournament");
                call(`tournament/delete/${this.routeParams.id}/`, 'DELETE').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
            else {
                call(`tournament/leave/${this.routeParams.id}/`, 'DELETE').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
        },

        subscribeStartTournamentButtonAction() {
            if (this.data.tournamentState !== "setup")
                return;
            if (this.data.clientRole === "admin") {
                console.log("starting tournament");
                call(`tournament/start/${this.routeParams.id}/`, 'PUT').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
            else {
                call(`tournament/join/${id}/`, 'PUT').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
        },

        leaveLobbyButtonAction() {
            router("/home");
        },

       
        // buildParticipantsList(list) {
        //     //console.log("Building participants list from list: ", list);
        //     const mainDiv = this.domManip.$id("tournament-list");
        //     for (let element of list){
        //         //console.log("participant card:", particpantCard);
        //         mainDiv.appendChild(createParticipantCard(element));
        //     }
        // },

        // joinTournament() {
        //     console.log("Joining tournament");
        //     const id = 5;   // TODO: MAKE IT COME FROM THE URL
        //     call(`tournament/join/${id}/`, 'PUT').then(data => {
        //         console.log(data);
        //         $callToast("success", data.message);
        //     })
        //     this.domManip.$id("join-button").style.display = "none";
        //     this.domManip.$id("leave-button").style.display = "block";
        // },

        // leaveTournament() {
        //     console.log("Leaving tournament");
        //     const id = 5;   // TODO: MAKE IT COME FROM THE URL
        //     call(`tournament/leave/${id}/`, 'DELETE').then(data => {
        //         console.log(data);
        //         $callToast("success", data.message);
        //     })
        //     this.domManip.$id("leave-button").style.display = "none";
        //     this.domManip.$id("join-button").style.display = "block";
        // },

        // startTournament() {
        //     console.log("Starting tournament");
        //     const id = 5;   // TODO: MAKE IT COME FROM THE URL
        //     call(`tournament/start/${id}/`, 'PUT').then(data => {
        //         console.log(data);
        //         $callToast("success", data.message);
        //     })
        // },

        // cancelTournament() {
        //     console.log("Cancelling tournament");
        //     const id = 5;   // TODO: MAKE IT COME FROM THE URL
        //     call(`tournament/delete/${id}/`, 'DELETE').then(data => {
        //         console.log(data);
        //         $callToast("success", data.message);
        //     })
        // }
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            // this.domManip.$off(this.domManip.$id("join-button"), "click", this.joinTournament);
            // this.domManip.$off(this.domManip.$id("leave-button"), "click", this.leaveTournament);
            // this.domManip.$off(this.domManip.$id("start-button"), "click", this.startTournament);
            // this.domManip.$off(this.domManip.$id("cancel-button"), "click", this.cancelTournament);
            // WebSocketManager.setCurrentRoute(undefined);
        
        
            this.domManip.$off(this.domManip.$id("tournament-leave-to-lobby"), "click", this.leaveLobbyButtonAction);
            this.domManip.$off(this.domManip.$id("tournament-middle-bottom-subscribe-start-button"), "click", this.subscribeStartTournamentButtonAction);
            this.domManip.$off(this.domManip.$id("tournament-quit-cancel-button"), "click", this.quitCancelTournamentButtonAction);
            this.domManip.$off(this.domManip.$id("tournament-games-do-come-button"), "click", this.openCurrentGames);
            this.domManip.$off(this.domManip.$id("tournament-rank-button"), "click", this.openTournamentRank);
            this.domManip.$off(this.domManip.$id("tournament-history-button"), "click", this.openTournamentHistory);
            
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            WebSocketManager.setCurrentRoute("tournament");
            call(`tournament/lobby/${this.routeParams.id}/`, 'GET').then(data => {
                console.log("data:", data);
                this.data = data;


                buildView(data.tournamentState);

                if (data.tournamentState === "setup") {
                    for (let element of data.tournamentMembers)
                        createPlayerCard(element);
                }

                this.domManip.$on(this.domManip.$id("tournament-leave-to-lobby"), "click", this.leaveLobbyButtonAction);
                this.domManip.$on(this.domManip.$id("tournament-middle-bottom-subscribe-start-button"), "click", this.subscribeStartTournamentButtonAction);
                this.domManip.$on(this.domManip.$id("tournament-quit-cancel-button"), "click", this.quitCancelTournamentButtonAction);
                this.domManip.$on(this.domManip.$id("tournament-games-do-come-button"), "click", this.openCurrentGames);
                this.domManip.$on(this.domManip.$id("tournament-rank-button"), "click", this.openTournamentRank);
                this.domManip.$on(this.domManip.$id("tournament-history-button"), "click", this.openTournamentHistory);
            })


            // const id = 5;  // TODO: MAKE IT COME FROM THE URL
            // call(`tournament/lobby/${id}/`, 'GET').then(data => {
            //     //console.log(data);
            //     let stateColor;
            //     if (data.tournamentState == "setup")
            //         stateColor = "orange";
            //     else if (data.tournamentState == "ongoing")
            //         stateColor = "green";
            //     else
            //         stateColor = "red";
            //     this.domManip.$id("status").style.backgroundColor = stateColor;
            //     this.domManip.$id("status").textContent = "State: " + data.tournamentState;
            //     this.domManip.$id("tournament-name").textContent = "Tournament Name: " + data.tournamentName;
            //     this.domManip.$id("client-role").textContent = "Client Role: " + data.clientRole;

            //     this.buildParticipantsList(data.tournamentMembers);

            //     this.domManip.$on(this.domManip.$id("join-button"), "click", this.joinTournament);
            //     this.domManip.$on(this.domManip.$id("leave-button"), "click", this.leaveTournament);
            //     this.domManip.$on(this.domManip.$id("start-button"), "click", this.startTournament);
            //     this.domManip.$on(this.domManip.$id("cancel-button"), "click", this.cancelTournament);
            //     this.domManip.$id("leave-button").style.display = "none";
            // })
        },
    }
}