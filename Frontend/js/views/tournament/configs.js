import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
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
        callbackRankButton(event) {
            console.warn(event);
            this.changeTabs(event.srcElement.getAttribute("tab"));
        },
        changeTabs(tab) {
            /* ALLOWED TABS ARE: participants games-upcoming games-finished rank */
            const container = this.domManip.$id("container-" + tab);
            if (!container) {
                console.warn("Tab not found:", tab);
                return;
            }
            // Hide all tabs
            this.domManip.$id("container-participants").style.display = "none";
            this.domManip.$id("container-rank").style.display = "none";
            this.domManip.$id("container-games-upcoming").style.display = "none";
            this.domManip.$id("container-games-finished").style.display = "none";
            // Show the selected tab
            container.style.display = "block";
        },

        /* API CALLS */
        joinTournament() {
            // TODO:
        },
        leaveTournament() {
            // TODO:
        },
        startTournament() {
            // TODO:
        },
        cancelTournament() {
            // TODO:
        },

        leaveLobby() {
            router("/home");
        },

    },

    hooks: {
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                router('/404');
                return;
            }
            WebSocketManager.setCurrentRoute("tournament");
            call(`tournament/lobby/${this.routeParams.id}/`, 'GET').then(data => {
                console.log("data:", data);
                this.data = data;

                tournamentData.isPublic = data.tournamentPublic;


                //buildView(data.tournamentInfo.state);

                if (data.tournamentInfo.state === "setup") {
                    for (let element of data.tournamentMembers)
                        createPlayerCard(element);
                    this.changeTabs("participants");
                }
                // TODO: uncomment this
                /* else {
                    if (data.tournamentMembers.length == 3)
                        updatePodium(data.tournamentMembers.find(member => member.rank === 3), "third", false);
                    for (let element of data.tournamentGames) {
                        createGameCard(element);
                        updateFinalsDiagram(element);
                    }
                }

                if (data.tournamentInfo.state !== "setup")
                    updateRankTable(data.tournamentMembers);


                EventListenerManager.linkEventListener("tournament-leave-to-lobby",                         "tournament", "click", this.leaveLobbyButtonAction);
                EventListenerManager.linkEventListener("button-subscribe-start",   "tournament", "click", this.subscribeStartTournamentButtonAction);
                EventListenerManager.linkEventListener("button-unsubscribe-cancel",                     "tournament", "click", this.quitCancelTournamentButtonAction);
                EventListenerManager.linkEventListener("tournament-games-do-come-button",                   "tournament", "click", this.openCurrentGames);
                EventListenerManager.linkEventListener("tournament-rank-button",                            "tournament", "click", this.openTournamentRank);
                EventListenerManager.linkEventListener("tournament-history-button",                         "tournament", "click", this.openTournamentHistory);
                EventListenerManager.linkEventListener("tournament-go-to-current-game-button",              "tournament", "click", this.routeToCurrentGame);
                EventListenerManager.linkEventListener("tournament-round-robbin-button",                    "tournament", "click", this.openRoundRobbinTable);
                EventListenerManager.linkEventListener("tournament-finals-button",                          "tournament", "click", this.openFinalsTable); */




                EventListenerManager.linkEventListener("button-tab-rank",           "tournament", "click", this.callbackRankButton);
                EventListenerManager.linkEventListener("button-tab-games-finished", "tournament", "click", this.callbackRankButton);
                EventListenerManager.linkEventListener("button-tab-games-upcoming", "tournament", "click", this.callbackRankButton);
            }).catch(err => {
                console.log(err);
                router("/404", {msg: err.message});
            }
            );
        },
    }
}