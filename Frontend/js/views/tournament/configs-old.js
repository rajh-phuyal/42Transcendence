import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import router from '../../navigation/router.js';
// import { createParticipantCard } from './methods.js';
import { buildView, createPlayerCard, createGameCard, updateRankTable, updateFinalsDiagram, updatePodium } from './methods-old.js';
import { tournamentData } from './objects.js';


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
            if (this.data.tournamentInfo.state !== "setup")
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
            if (this.data.tournamentInfo.state !== "setup")
                return;
            if (this.data.clientRole === "admin") {
                console.log("starting tournament");
                call(`tournament/start/${this.routeParams.id}/`, 'PUT').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
            else {
                call(`tournament/join/${this.routeParams.id}/`, 'PUT').then(data => {
                    console.log(data);
                    $callToast("success", data.message);
                })
            }
        },

        routeToCurrentGame() {
            console.log("routing to current games");
            call('tournament/go-to-game/', 'GET').then(data => {
                console.log(data);
                router(`/game`, { id: data.id });
            })
        },

        leaveLobbyButtonAction() {
            router("/home");
        },

        openRoundRobbinTable() {
            console.log("opening round robbin table");

            this.domManip.$id("tournament-round-robbin-container").style.display = "flex";
            this.domManip.$id("tournament-finals-container").style.display = "none";
            this.domManip.$id("tournament-round-robbin-button").setAttribute("color", "#7B0101");
            this.domManip.$id("tournament-finals-button").setAttribute("color", "black");
        },

        openFinalsTable() {
            console.log("opening finals table");

            this.domManip.$id("tournament-round-robbin-container").style.display = "none";
            this.domManip.$id("tournament-finals-container").style.display = "block";
            this.domManip.$id("tournament-round-robbin-button").setAttribute("color", "black");
            this.domManip.$id("tournament-finals-button").setAttribute("color", "#7B0101")
        }

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            WebSocketManager.setCurrentRoute(undefined);
            this.domManip.$off(this.domManip.$id("tournament-leave-to-lobby"), "click", this.leaveLobbyButtonAction);
            this.domManip.$off(this.domManip.$id("button-subscribe-start"), "click", this.subscribeStartTournamentButtonAction);
            this.domManip.$off(this.domManip.$id("button-unsubscribe-cancel"), "click", this.quitCancelTournamentButtonAction);
            this.domManip.$off(this.domManip.$id("tournament-games-do-come-button"), "click", this.openCurrentGames);
            this.domManip.$off(this.domManip.$id("tournament-rank-button"), "click", this.openTournamentRank);
            this.domManip.$off(this.domManip.$id("tournament-history-button"), "click", this.openTournamentHistory);
            this.domManip.$off(this.domManip.$id("tournament-go-to-current-game-button"), "click", this.routeToCurrentGame);
            this.domManip.$off(this.domManip.$id("tournament-round-robbin-button"), "click", this.openRoundRobbinTable);
            this.domManip.$off(this.domManip.$id("tournament-finals-button"), "click", this.openFinalsTable);
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {

        },
    }
}