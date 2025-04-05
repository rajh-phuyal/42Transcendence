import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import { audioPlayer } from '../../abstracts/audio.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import { updateView } from './methodsView.js';
import { tournamentData } from './objects.js';
import { callbackTabButton } from './callbacks.js';
import { clearAllGameDeadlines } from './methodsGames.js';
import { updatePodium, updateFinalsDiagram } from './methodsRankFinals.js';

export default {
    attributes: {
    },

    methods: {
        initObjects() {
            tournamentData.clientRole          = undefined;
            tournamentData.tournamentInfo      = undefined;
            tournamentData.tournamentMembers   = undefined;
            tournamentData.tournamentGames     = undefined;
            tournamentData.podiumMembers       = [];
        },

        routeToHome() {
            router('/');
        },
    },

    hooks: {
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            clearAllGameDeadlines();
            this.initObjects();
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                router('/404');
                return;
            }
            // Reset the tournamentData object
            this.initObjects();
            // Start music
            audioPlayer.playMusic("lobbyTournament");
            // Add all event listeners
            EventListenerManager.linkEventListener("button-tab-members",          "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-finals",           "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-round-robin",      "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-games-upcoming",   "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-tab-games-finished",   "tournament", "click", callbackTabButton);
            EventListenerManager.linkEventListener("button-leave-lobby",          "tournament", "click", this.routeToHome);

            // Fetch the data from the API
            call(`tournament/lobby/${this.routeParams.id}/`, 'GET').then(data => {
                // Store the data in the object
                tournamentData.clientRole           = data.clientRole
                tournamentData.tournamentInfo       = data.tournamentInfo
                tournamentData.tournamentMembers    = data.tournamentMembers
                tournamentData.tournamentGames      = data.tournamentGames
                // XICOS FINALS LOGIC:
                if (data.tournamentMembers.length == 3)
                    updatePodium(data.tournamentMembers.find(member => member.rank === 3), "third", false);
                for (let element of data.tournamentGames)
                    updateFinalsDiagram(element);
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