import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { changeGameState, updateReadyStateNodes } from './methods.js';
import { toggleGamefieldVisible, gameRender } from './render.js';
import { gameObject } from './objects.js';
import { endGameLoop } from './loop.js';

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
        playAgainCallback() {
            call(`game/play-again/${this.gameId}/`, 'PUT').then(data => {
                console.log("data:", data);
                if (data.status === "success" && data.gameId) {
                    // Reload the game
                    router(`/game`, {id: data.gameId});
                }
            })
        },
        menuKeysCallback(event) {
            switch (event.key) {
                case " ":
                    // Only if no connection exists and
                    // game state is pending, ongoing or paused, open the WS connection
                    if (!gameObject.wsConnection && gameObject.state === "pending" || gameObject.state === "ongoing" || gameObject.state === "paused" || gameObject.state === "countdown") {
                        try {
                            this.domManip.$id("game-view-middle-side-container-top-text").innerText="";
                            gameObject.playerLeft.state = "waiting";
                            gameObject.playerRight.state = "waiting";
                            updateReadyStateNodes();
                            WebSocketManagerGame.connect(this.gameId);
                            gameObject.wsConnection = true;
                            // TODO #304 this should be done by the animaion
                            const gameViewImageContainer = this.domManip.$id("game-view-image-container");
                            gameViewImageContainer.style.backgroundImage = "none";
                            gameViewImageContainer.style.width= "100%";
                        }
                        catch (error) {
                            this.domManip.$id("game-view-middle-side-container-top-text").innerText = translate("game", "connection-error");
                        }
                    }
                    break;
                case "Escape":
                    // Quit the game
                    router('/');
                default:
                    return;
            }
        },
        initListeners(init = true) {
            const buttonLeaveLobby = this.domManip.$id("button-leave-lobby");
            const buttonQuitGame = this.domManip.$id("button-quit-game");
            const buttonPlayAgain = this.domManip.$id("button-play-again");

            if (init) {
                // TODO: translation for buttons should be done in with the abstraction tool TBC
                buttonLeaveLobby.name = translate("game", "button-leave-lobby");
                buttonLeaveLobby.render();
                buttonQuitGame.name = translate("game", "button-quit-game");
                buttonQuitGame.render();
                buttonPlayAgain.name = translate("game", "button-play-again");
                buttonPlayAgain.render();
                this.domManip.$on(buttonLeaveLobby, "click", this.leaveLobbyCallback);
                this.domManip.$on(buttonQuitGame, "click", this.quitGameCallback);
                this.domManip.$on(buttonPlayAgain, "click", this.playAgainCallback);
                this.domManip.$on(document, 'keydown', this.menuKeysCallback);
                return ;
            }

            if (!init) {
                if (buttonLeaveLobby) {
                    // Remove the event listener if exists
                    if (buttonLeaveLobby.eventListeners)
                        this.domManip.$off(buttonLeaveLobby, "click");
                    if (buttonQuitGame.eventListeners)
                        this.domManip.$off(buttonQuitGame, "click");
                    if (buttonPlayAgain.eventListeners)
                        this.domManip.$off(buttonPlayAgain, "click");
                    if (document.eventListeners)
                        this.domManip.$on(document, 'keydown', this.menuKeysCallback);
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
                    gameObject.mapId = data.gameData.mapNumber;
                    this.mapId = data.gameData.mapNumber;

                    // I send the ready state also via REST NOW
                    // TODO: but i guess this could go in a function thath is also called by the WSManager
                    gameObject.playerRight.state = data.playerRight.ready ? "ready" : undefined;
                    gameObject.playerLeft.state = data.playerLeft.ready ? "ready" : undefined;

                    changeGameState(data.gameData.state);
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
            gameObject.wsConnection = false;
            gameObject.state = undefined;
            gameObject.frameTime = 1000/15; // NOTE: this means 15 frames per second which should match the backend FPS
            gameObject.lastFrameTime = 0;
            gameObject.animationId = null;
            gameObject.sound = null;
            gameObject.playerInputLeft.paddleMovement = 0;
            gameObject.playerInputLeft.powerupSpeed = false;
            gameObject.playerInputLeft.powerupBig = false;
            gameObject.playerInputRight.paddleMovement = 0;
            gameObject.playerInputRight.powerupFast = false;
            gameObject.playerInputRight.powerupSpeed = false;
            gameObject.playerLeft.state = undefined;
            gameObject.playerLeft.points = 0
            gameObject.playerLeft.pos = 50;
            gameObject.playerLeft.size = 10;
            gameObject.playerLeft.powerupBig = "unavailable";
            gameObject.playerLeft.powerupSlow = "unavailable";
            gameObject.playerLeft.powerupFast = "unavailable";
            gameObject.playerLeft.points = 0
            gameObject.playerRight.state = undefined;
            gameObject.playerRight.pos = 50;
            gameObject.playerRight.size = 10;
            gameObject.playerRight.powerupBig = "unavailable";
            gameObject.playerRight.powerupSlow = "unavailable";
            gameObject.playerRight.powerupFast = "unavailable";
			gameObject.ball.posX = 50;
			gameObject.ball.posY = 50;
            // Before loading sed the game avatars to default avatar:
            this.domManip.$id("player-left-avatar").src = window.origin + '/media/avatars/54c455d5-761b-46a2-80a2-7a557d9ec618.png';
            this.domManip.$id("player-right-avatar").src = window.origin + '/media/avatars/54c455d5-761b-46a2-80a2-7a557d9ec618.png';

        },

        setMapImage() {
            const mapName = this.maps[this.mapId];
            const gameImage = this.domManip.$id("game-view-map-image").children[0];
            const gameField = this.domManip.$id("game-field");
            const filePath = window.location.origin + '/assets/game/maps/' + mapName + '.png';
            gameImage.src = filePath;
            gameImage.style.display = "block";
            gameField.style.display = "block";
        }
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            WebSocketManagerGame.disconnect(this.gameId);
            this.initListeners(false);
            endGameLoop();
            this.audioPlayer.stop();
        },

        beforeDomInsertion() {

        },

        async afterDomInsertion() {
            this.initListeners();
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                console.warn("Invalid game id '%s' from routeParams?.id -> redir to home", this.routeParams.id);
                router('/');
                return;
            }
            // Setting the gameId from the route params
            this.gameId = this.routeParams.id;
            // Initialize the game object
            this.initObjects();
            // Initialize the first view (before loading actuall game data)
            changeGameState(undefined);
            // REST call to load the game details
            await this.loadDetails()
            this.setMapImage();
            // Show filed TODO: this should not happen right away!
            toggleGamefieldVisible(true);
		}
    }
}