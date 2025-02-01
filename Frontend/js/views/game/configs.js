import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';

export default {
    attributes: {
        gameId: null,
        map: undefined,

        maps: {
            "ufo": 1,
            "lizard-people": 2,
            "snowman": 3,
            "lochness": 4,
        },
    },

    methods: {
        leaveLobbyCallback() {
            router('/');
        },

        quitGameCallback() {
            // Quit game
            call(`game/delete/${this.gameId}/`, 'DELETE').then(data => {
                router('/');
            })
        },

        initListeners(init = true) {
            const buttonLeaveLobby = this.domManip.$id("button-leave-lobby");
            const buttonQuitGame = this.domManip.$id("button-quit-game");

            if (init) {
                // TODO: translation for buttons should be done in with the abstraction tool TBC
                buttonLeaveLobby.name = translate("game", "button-leave-lobby");
                buttonLeaveLobby.render();
                buttonQuitGame.name = translate("game", "button-quit-game");
                buttonQuitGame.render();
                this.domManip.$on(buttonLeaveLobby, "click", this.leaveLobbyCallback);
                this.domManip.$on(buttonQuitGame, "click", this.quitGameCallback);
                return ;
            }

            if (!init) {
                if (buttonLeaveLobby) {
                    // Remove the event listener if exists
                    if (buttonLeaveLobby.eventListeners)
                        this.domManip.$off(buttonLeaveLobby, "click");
                    if (buttonQuitGame.eventListeners)
                        this.domManip.$off(buttonQuitGame, "click");
                }
            }
        },
        
        async loadDetails() {
            // Load the data from REST API
            return call(`game/lobby/${this.gameId}/`, 'GET')
                .then(data => {
                    console.log("data:", data);

                    // Set user cards
                    this.domManip.$id("player-left-username").innerText = "@" + data.playerLeft.username
                    this.domManip.$id("player-left-avatar").src = window.origin + '/media/avatars/' + data.playerLeft.avatar
                    this.domManip.$id("player-right-username").innerText = "@" + data.playerRight.username
                    this.domManip.$id("player-right-avatar").src = window.origin + '/media/avatars/' + data.playerRight.avatar

                    this.map = this.maps[data.gameData.mapNumber];
                })
                .catch(error => {
                    router('/');
                    console.error('Error occurred:', error);
                });
        },
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            WebSocketManagerGame.disconnect(this.gameId);
            this.initListeners(false);
        },

        beforeDomInsertion() {

        },

        async afterDomInsertion() {
            this.initListeners();

            // Checking game id
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                console.warn("Invalid game id '%s' from routeParams?.id -> redir to home", this.routeParams.id);
                router('/');
                return;
            }
            this.gameId = this.routeParams.id;
            await this.loadDetails()

            // Connect to Websocket
            WebSocketManagerGame.connect(this.gameId);
        },
    }
}