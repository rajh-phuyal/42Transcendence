import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import { changeGameState } from './methods.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';

export default {
    attributes: {
        gameId: null,
        loading: false,
        map: undefined,

        maps: {
            "ufo": 1,
            "lizard-people": 2,
            "snowman": 3,
            "lochness": 4,
        },
    },

    methods: {
        listenerLeaveLobby() {
            // TODO: Close WS connection
            // redir home
            router('/');
        },

        listenerQuitGame() {
            // TODO:Check if allowed to quit
                // Quit game
                call(`game/delete/${this.gameId}/`, 'DELETE')
                // Close WS connection
                // Redir home
                router('/');
        },

        initListeners(init = true) {
            const buttonLeaveLobby = this.domManip.$id("button-leave-lobby");
            const buttonQuitGame = this.domManip.$id("button-quit-game");
            if (!buttonLeaveLobby || !buttonQuitGame) {
                console.warn("Button not found. Please check the button id.");
                return;
            }

            if (init) {
                buttonLeaveLobby.name = translate("game", "button-leave-lobby");
                buttonLeaveLobby.render();
                buttonQuitGame.name = translate("game", "button-quit-game");
                buttonQuitGame.render();
                this.domManip.$on(buttonLeaveLobby, "click", this.listenerLeaveLobby);
                this.domManip.$on(buttonQuitGame, "click", this.listenerQuitGame);
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
        initAndTranslate() {
            // Set default values
            // TODO: we should store the default avatar filename somwhere i guess
            // Player 1
            this.domManip.$id("player-left-avatar").src = window.origin + '/media/avatars/' + '54c455d5-761b-46a2-80a2-7a557d9ec618.png'
            this.domManip.$id("player-left-username").innerText = translate("game", "loading...")

            // Player 2
            this.domManip.$id("player-right-avatar").src = window.origin + '/media/avatars/' + '54c455d5-761b-46a2-80a2-7a557d9ec618.png'
            this.domManip.$id("player-right-username").innerText = translate("game", "loading...")

        },

        async loadDetails() {
            // To avoid multiple calls at the same time
            if(this.loading) {
                console.warn("Already loading view. Please wait.");
                return Promise.resolve();
            }
            this.loading = true;

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
                    
                    // Set game state
                    changeGameState(data.gameState);

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
            // Disconnect from Websocket
            // Connect to Websocket
            WebSocketManagerGame.disconnect(this.gameId);

            this.initListeners(false);
        },

        beforeDomInsertion() {

        },

        async afterDomInsertion() {
            this.initAndTranslate();
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

            // Hide the spinner and show conncted message
            this.domManip.$id("player-left-state-spinner").style.display = "none";
            this.domManip.$id("player-left-state").innerText = translate("game", "ready");
        },
    }
}