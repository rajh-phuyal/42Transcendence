import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { changeGameState, drawPlayersState } from './methods.js';
import { gameObject } from './objects.js';
import { endGameLoop } from './loop.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';

export default {
    attributes: {
        gameId: null,
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
                if (gameObject.state === "pending")
                    router('/');
                else
                    router(`/game`, {id: this.gameId});
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
                    // If game is finished the space key will create a new game
                    console.log("gameObject.state:", gameObject.state);
                    if (gameObject.state === "finished" || gameObject.state === "quited")
                       this.playAgainCallback();
                    // Only if no connection exists and
                    // game state is pending, ongoing or paused, open the WS connection
                    if (!gameObject.wsConnection && (gameObject.state === "pending" || gameObject.state === "ongoing" || gameObject.state === "paused" || gameObject.state === "countdown")) {
                        gameObject.playerLeft.state = "waiting";
                        gameObject.playerRight.state = "waiting";
                        drawPlayersState();
                        WebSocketManagerGame.connect(this.gameId)
                            .then(() => {
                                gameObject.wsConnection = true;
                                // Since the viewer could enter whenever we need to check if the game is already ongoing
                                // and if so we need to start the game loop
                                if (!gameObject.clientIsPlayer) {
                                    if (gameObject.state === "ongoing")
                                        startGameLoop();
                                    else
                                        changeGameState("pending");
                                }
                            })
                            .catch(error => {
                                this.domManip.$id("game-view-middle-side-container-top-text").innerText = translate("game", "connection-error");
                            });
                    }
                    break;
                case "Escape":
                    // Quit the game
                    router('/');
                default:
                    return;
            }
        },

        mentionClickCallback(event) {
            const mention = event.target.closest(".mention-user");
            const tournament = event.target.closest(".mention-tournament");

            // Check if a mention USER was clicked
            if (mention) {
                const userId = mention.getAttribute("data-userid");
                if (userId)
                    router(`/profile`, { id: userId });
                else
                    console.warn("Mention clicked but no user ID found.");
            }

            // Check if a mention TOURNAMENT was clicked
            if (tournament) {
                const tournamentId = tournament.getAttribute("data-tournamentid");
                if (tournamentId)
                    router(`/tournament`, { id: tournamentId });
                else
                    console.warn("Mention clicked but no tournament ID found.");
            }

        },

        initListeners() {
            // TODO: translation for buttons should be done in with the abstraction tool TBC
            this.domManip.$id("button-play-again").innerText = translate("game", "button-play-again");
            this.domManip.$id("button-leave-lobby").innerText = translate("game", "button-leave-lobby");
            this.domManip.$id("button-quit-game").innerText = translate("game", "button-quit-game");
            EventListenerManager.linkEventListener("button-leave-lobby",        "game", "click",    this.leaveLobbyCallback);
            EventListenerManager.linkEventListener("button-quit-game",          "game", "click",    this.quitGameCallback);
            EventListenerManager.linkEventListener("button-play-again",         "game", "click",    this.playAgainCallback);
            EventListenerManager.linkEventListener("barely-a-body",             "game", "keydown",  this.menuKeysCallback);
            EventListenerManager.linkEventListener("player-left-username",      "game", "click",    this.mentionClickCallback);
            EventListenerManager.linkEventListener("player-left-avatar",        "game", "click",    this.mentionClickCallback);
            EventListenerManager.linkEventListener("player-right-username",     "game", "click",    this.mentionClickCallback);
            EventListenerManager.linkEventListener("player-right-avatar",       "game", "click",    this.mentionClickCallback);
            EventListenerManager.linkEventListener("game-view-tournament-name", "game", "click",    this.mentionClickCallback);
        },

        async loadDetails() {
            // Load the data from REST API
            return call(`game/lobby/${this.gameId}/`, 'GET')
                .then(data => {
                    console.log("data:", data);

                    // Set user cards
                    this.domManip.$id("player-left-username").innerText = data.playerLeft.username;
                    this.domManip.$id("player-left-username").setAttribute("data-userid", data.playerLeft.userId);
                    this.domManip.$id("player-left-avatar").src = window.origin + '/media/avatars/' + data.playerLeft.avatar
                    this.domManip.$id("player-left-avatar").setAttribute("data-userid", data.playerLeft.userId);
                    this.domManip.$id("player-right-username").innerText = data.playerRight.username;
                    this.domManip.$id("player-right-username").setAttribute("data-userid", data.playerRight.userId);
                    this.domManip.$id("player-right-avatar").src = window.origin + '/media/avatars/' + data.playerRight.avatar
                    this.domManip.$id("player-right-avatar").setAttribute("data-userid", data.playerRight.userId);

                    // Set game data
                    gameObject.clientIsPlayer = data.gameData.clientIsPlayer;
                    gameObject.playerLeft.points = data.playerLeft.points;
                    gameObject.playerLeft.result = data.playerLeft.result;
                    gameObject.playerRight.points = data.playerRight.points;
                    gameObject.playerRight.result = data.playerRight.result;
                    gameObject.mapName = this.maps[data.gameData.mapNumber];

                    // Check if game is part of tournament
                    if (data.gameData.tournamentId) {
                        gameObject.tournamentId = data.gameData.tournamentId;
                        this.domManip.$id("game-view-tournament-name").innerText = translate("game", "partOfTournament") + data.gameData.tournamentName;
                        this.domManip.$id("game-view-tournament-name").setAttribute("data-tournamentid", data.gameData.tournamentId);
                        this.domManip.$id("game-view-tournament-name").style.display = "block";
                    }

                    // I send the ready state also via REST NOW
                    gameObject.playerRight.state = data.playerRight.ready ? "ready" : undefined;
                    gameObject.playerLeft.state = data.playerLeft.ready ? "ready" : undefined;

                    // The state should never be "ongoing" when the game is loaded
                    if (data.gameData.state === "ongoing")
                        data.gameData.state = "paused";
                    changeGameState(data.gameData.state);
                })
                .catch(error => {
                    router('/404', {msg: error.message});
                });
        },

        initObjects() {
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
        },
    },

    hooks: {
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            // In case the countdown is still running, we need to stop it
            if (gameObject.countDownInterval) {
                clearInterval(gameObject.countDownInterval);
                gameObject.countDownInterval = undefined;
                this.domManip.$id("game-countdown-image").style.display = "none";
            }
            endGameLoop();
            this.audioPlayer.stop();
            WebSocketManagerGame.disconnect(this.gameId)
        },

        beforeDomInsertion() {
        },

        async afterDomInsertion() {
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                router('/404');
                return;
            }
            // Initialize the event listeners
            this.initListeners();
            // Setting the gameId from the route params
            this.gameId = this.routeParams.id;
            // Initialize the game object
            this.initObjects();
            // Initialize the first view (before loading actuall game data)
            changeGameState(undefined);
            // REST call to load the game details
            await this.loadDetails()
		}
    }
}