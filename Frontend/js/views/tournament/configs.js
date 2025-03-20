import { audioPlayer } from '../../abstracts/audio.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';
// import { createParticipantCard } from './methods.js';
import { initView, updateView } from './methodsView.js';
import { tournamentData } from './objects.js';
import { callbackTabButton } from './callbacks.js';
import { clearAllGameCountdowns } from './methodsGames.js';
import { updatePodium, updateFinalsDiagram } from './methodsRankFinals.js';

export default {
    attributes: {
        data: undefined,
    },

    methods: {
        routeToCurrentGame() {
            call('tournament/go-to-game/', 'GET').then(data => {
                router(`/game`, { id: data.id });
            })
        },
    },

    hooks: {
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            clearAllGameCountdowns();
            audioPlayer.stop();
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                router('/404');
                return;
            }
            // Start music
            audioPlayer.play(5); // Lobby music for tournaments
            // Add all event listeners
            EventListenerManager.linkEventListener("button-tab-members",          "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-finals",           "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-round-robin",      "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-games-upcoming",   "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-games-finished",   "tournament", "click", callbackTabButton);


// TODO: revise the listeners below
            //EventListenerManager.linkEventListener("tournament-leave-to-lobby",                         "tournament", "click", this.leaveLobbyButtonAction);
            //EventListenerManager.linkEventListener("button-start",   "tournament", "click", this.subscribeStartTournamentButtonAction);
            //EventListenerManager.linkEventListener("button-unsubscribe-cancel",                     "tournament", "click", this.quitCancelTournamentButtonAction);
            //EventListenerManager.linkEventListener("tournament-games-do-come-button",                   "tournament", "click", this.openCurrentGames);
            //EventListenerManager.linkEventListener("tournament-rank-button",                            "tournament", "click", this.openTournamentRank);
            //EventListenerManager.linkEventListener("tournament-history-button",                         "tournament", "click", this.openTournamentHistory);
            //EventListenerManager.linkEventListener("tournament-go-to-current-game-button",              "tournament", "click", this.routeToCurrentGame);
            //EventListenerManager.linkEventListener("tournament-round-robbin-button",                    "tournament", "click", this.openRoundRobbinTable);
            //EventListenerManager.linkEventListener("tournament-finals-button",                          "tournament", "click", this.openFinalsTable);

            // Fetch the data from the API
            call(`tournament/lobby/${this.routeParams.id}/`, 'GET').then(data => {
                // Store the data in the object

                tournamentData.clientRole           = data.clientRole
                tournamentData.tournamentInfo       = data.tournamentInfo
                tournamentData.tournamentMembers    = data.tournamentMembers
                tournamentData.tournamentGames      = data.tournamentGames
                console.log("API DATA LOBBY:", data);
                // XICOS FINALS LOGIC:
                console.warn("XICOS FINALS LOGIC:", data.tournamentMembers);
                if (data.tournamentMembers.length == 3)
                    updatePodium(data.tournamentMembers.find(member => member.rank === 3), "third", false);
                for (let element of data.tournamentGames)
                    updateFinalsDiagram(element);
                // Initialize all view elements (usercards, gamecards, etc)
                initView();
                // Update the view
                updateView();

            }).catch(err => {
                console.log(err);
                router("/404", {msg: err.message});
            }
            );
        },
    }
}