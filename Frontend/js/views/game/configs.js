import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { endGameLoop, changeGameState, showPowerupStatus } from './methods.js';
import { gameRender } from './render.js';
import { gameObject } from './objects.js';
import AudioPlayer from '../../abstracts/audio.js';

export default {
    attributes: {
        gameId: null,
        mapId: undefined,

        maps: {
            1: "ufo",
            2: "lizard-people",
            3: "snowman",
            4: "lochness",
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

                    // Set game data
                    gameObject.playerLeft.points = data.playerLeft.points;
                    gameObject.playerRight.points = data.playerRight.points;
                    this.mapId = data.gameData.mapNumber;

                    // I send the ready state also via REST NOW
                    // TODO: but i guess this could go in a function thath is also called by the WSManager
                    if (data.playerLeft.ready) {
                        this.domManip.$id("player-left-state-spinner").style.display = "none";
                        this.domManip.$id("player-left-state").style.display = "block";
                    }
                    else {
                        this.domManip.$id("player-left-state-spinner").style.display = "block";
                        this.domManip.$id("player-left-state").style.display = "none";
                    }
                    if (data.playerRight.ready) {
                        this.domManip.$id("player-right-state-spinner").style.display = "none";
                        this.domManip.$id("player-right-state").style.display = "block";
                    }
                    else {
                        this.domManip.$id("player-right-state-spinner").style.display = "block";
                        this.domManip.$id("player-right-state").style.display = "none";
                    }

                    // Set the map image
                    this.setMapImage();

                    // Set game state
                    changeGameState(data.gameData.state);

                    // Only if game state is pending, ongoing or paused, open the WS connection
                    if (data.gameData.state === "pending" || data.gameData.state === "ongoing" || data.gameData.state === "paused")
                        WebSocketManagerGame.connect(this.gameId);

                })
                .catch(error => {
                    router('/');
                    console.error('Error occurred:', error);
                });
        },
        initObjects() {
            // TODO: the game state should be set by the WSManager
            // Not sure if this TODO is correct.
            // THe initial load will only be done here
            // If a game is finished we will never opene a connection just show this default stuff
            // but with an updated score!
            gameObject.gameId = this.gameId;
            gameObject.frameTime = 1000/15; // NOTE: this means 15 frames per second which should match the backend FPS
            gameObject.state = "ongoing";
            gameObject.playerLeft.points = 0;
            gameObject.playerRight.points = 0;

            gameObject.playerLeft.pos = 50;
            gameObject.playerRight.pos = 50;

            gameObject.playerLeft.size = 10;
			gameObject.playerRight.size = 10;

			gameObject.ball.posX = 50;
			gameObject.ball.posY = 50;

            gameObject.playerLeft.powerups.big = "unavailable";  // available / using / used / unavailable
            gameObject.playerRight.powerups.big = "unavailable";
            gameObject.playerLeft.powerups.slow = "unavailable";
            gameObject.playerRight.powerups.slow = "unavailable";
            gameObject.playerLeft.powerups.fast = "unavailable";
            gameObject.playerRight.powerups.fast = "unavailable";
        },

        setMapImage() {
            const mapName = this.maps[this.mapId];
            console.log("mapId:", this.mapId, "mapName:", mapName);
            const filePath = window.location.origin + '/assets/game/maps/' + mapName + '.png';
            const gameViewImageContainer = this.domManip.$id("game-view-image-container");
            const gameImageContainer = this.domManip.$id("game-view-map-image");
            const gameImage = gameImageContainer.children[0];
            const gameField = this.domManip.$id("game-field");
            gameField.style.display = "block";
            gameImage.src = filePath;
            gameViewImageContainer.style.backgroundImage = "none";
            gameViewImageContainer.style.width= "100%";
            gameImage.style.display = "block";
        }
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            AudioPlayer.stop();
            WebSocketManagerGame.disconnect(this.gameId);
            this.initListeners(false);
            endGameLoop();
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
            this.initObjects();
            showPowerupStatus(false);
            await this.loadDetails()

			const gameField = this.domManip.$id("game-field");
			const ctx = gameField.getContext('2d');
			ctx.clearRect(0, 0, gameField.width, gameField.height);

			gameRender(gameField, ctx);

            //TODO: I uncommented the button so that for debung we always see the game field
            // related to issue: #304
			const goToGameButton = this.domManip.$id("go-to-game");
			goToGameButton.addEventListener('click', () => {
                // Start audio
                AudioPlayer.play(this.mapId);
            });
		},
    }
}