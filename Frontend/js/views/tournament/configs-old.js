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
                delete Tournament
            }
            else {
                leave tournament
            }
        },

        subscribeStartTournamentButtonAction() {
            if (this.data.tournamentInfo.state !== "setup")
                return;
            if (this.data.clientRole === "admin") {
                console.log("starting tournament");
                start toruunament
            }
            else {
                join tournament
            }
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

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {

        },
    }
}