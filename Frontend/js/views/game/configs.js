import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { changeGameState, drawPlayersState, clearAllGameDeadlines } from './methods.js';
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
                // console.log("data:", data);
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
                                this.domManip.$id("game-view-middle-side-container-top-text").innerText = translate("game", "connectionError");
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
                    gameObject.playerLeft.id = data.playerLeft.userId;
                    gameObject.playerRight.id = data.playerRight.userId;
                    gameObject.playerLeft.points = data.playerLeft.points;
                    gameObject.playerLeft.result = data.playerLeft.result;
                    gameObject.playerRight.points = data.playerRight.points;
                    gameObject.playerRight.result = data.playerRight.result;
                    gameObject.mapName = this.maps[data.gameData.mapNumber];
                    gameObject.deadline = data.gameData.deadline;

                    // Check if game is part of tournament
                    if (data.gameData.tournamentId) {
                        gameObject.tournamentId = data.gameData.tournamentId;
                        this.domManip.$id("game-view-tournament-name").innerText = translate("game", "partOfTournament") + data.gameData.tournamentName;
                        this.domManip.$id("game-view-tournament-name").setAttribute("data-tournamentid", data.gameData.tournamentId);
                        this.domManip.$id("game-view-tournament-name").style.display = "flex";
                    } else {
                        this.domManip.$id("game-view-tournament-name").style.display = "none";
                    }

                    // I send the ready state also via REST NOW
                    gameObject.playerRight.state = data.playerRight.ready ? "ready" : undefined;
                    gameObject.playerLeft.state = data.playerLeft.ready ? "ready" : undefined;

                    // The state should never be "ongoing" when the game is loaded
                    if (data.gameData.state === "ongoing")
                        data.gameData.state = "paused";
                    changeGameState(data.gameData.state);

                    // Show / Hide the controls
                    const controlsLeft = this.domManip.$id("player-left-controls");
                    const controlsRight = this.domManip.$id("player-right-controls");
                    // Hide by default
                    controlsLeft.style.display = "none";
                    controlsRight.style.display = "none";
                    // Show bottom border for player cards
                    const playerLeftBottomPiece = this.domManip.$class("lst")[0];
                    playerLeftBottomPiece.style.borderBottom = "0.3vw solid rgb(143, 148, 112)";
                    playerLeftBottomPiece.style.borderBottomLeftRadius = "3px";
                    playerLeftBottomPiece.style.borderBottomRightRadius = "3px";
                    const playerRightBottomPiece = this.domManip.$class("rst")[0];
                    playerRightBottomPiece.style.borderBottom = "0.3vw solid rgb(143, 148, 112)";
                    playerRightBottomPiece.style.borderBottomLeftRadius = "3px";
                    playerRightBottomPiece.style.borderBottomRightRadius = "3px";
                    // Show the controls if userid matches client if or is flatmate
                    const clientId = this.$store.fromState('user').id
                    // Show hide the controls | on local tournament games only the admin can see the controls
                    if (gameObject.clientIsPlayer && (gameObject.playerLeft.id == clientId || gameObject.playerLeft.id == 3)){
                        controlsLeft.style.display = "block";
                        playerLeftBottomPiece.style.borderBottom = "none";
                        playerLeftBottomPiece.style.borderBottomLeftRadius = "0px";
                        playerLeftBottomPiece.style.borderBottomRightRadius = "0px";
                    }
                    if (gameObject.clientIsPlayer && (gameObject.playerRight.id == clientId || gameObject.playerRight.id == 3)){
                        controlsRight.style.display = "block";
                        playerRightBottomPiece.style.borderBottom = "none";
                    playerRightBottomPiece.style.borderBottomLeftRadius = "0px";
                    playerRightBottomPiece.style.borderBottomRightRadius = "0px";
                    }
                })
                .catch(error => {
                    router('/404', {msg: error.message});
                });
        },

        initObjects() {
            gameObject.gameId = this.gameId;
            gameObject.countDownInterval = undefined;
            gameObject.tournamentId = undefined;
            gameObject.mapName = undefined;
            gameObject.wsConnection = false;
            gameObject.state = undefined;
            gameObject.frameTime = 1000/25; // NOTE = this means 25 frames per second which should match the backend FPS
            gameObject.lastFrameTime = 0;
            gameObject.animationId = undefined;
            gameObject.deadline = undefined;
            gameObject.sound = undefined;
            gameObject.paddleWidth = 1;     //  This means 1% of the game field width. If changed; also change the BE = PADDLE_OFFSET
            gameObject.paddleSpacing = 2;   //  This means 1% of the game field width is keept as a distance btween wall and paddle. If changed; also change the BE = PADDLE_OFFSET
            gameObject.borderStrokeWidth = 2;
            gameObject.clientIsPlayer = false; // Since all users can watch the lobby, this is used to determine if the client is a player or a spectator

            gameObject.playerInputLeft.paddleMovement = 0;
            gameObject.playerInputLeft.powerupSpeed = false;
            gameObject.playerInputLeft.powerupBig = false;

            gameObject.playerInputRight.paddleMovement = 0;
            gameObject.playerInputRight.powerupSpeed = false;
            gameObject.playerInputRight.powerupBig = false;

            gameObject.playerLeft.id = undefined;
            gameObject.playerLeft.state = undefined;
            gameObject.playerLeft.points = 0;
            gameObject.playerLeft.pos = 50;
            gameObject.playerLeft.size = 10;
            gameObject.playerLeft.result = undefined;
            gameObject.playerLeft.powerupBig = "unavailable";
            gameObject.playerLeft.powerupSlow = "unavailable";
            gameObject.playerLeft.powerupFast = "unavailable";

            gameObject.playerRight.id = undefined;
            gameObject.playerRight.state = undefined;
            gameObject.playerRight.points = 0;
            gameObject.playerRight.pos = 50;
            gameObject.playerRight.size = 10;
            gameObject.playerRight.result = undefined;
            gameObject.playerRight.powerupBig = "unavailable";
            gameObject.playerRight.powerupSlow = "unavailable";
            gameObject.playerRight.powerupFast = "unavailable";

            gameObject.ball.posX = 50;
            gameObject.ball.posY = 50;
            gameObject.ball.height = 1;
            gameObject.ball.width = 1;
        },
    },

    hooks: {
        beforeRouteEnter() {
            clearAllGameDeadlines();
        },

        beforeRouteLeave() {
            // In case the countdown is still running, we need to stop it
            if (gameObject.countDownInterval) {
                clearInterval(gameObject.countDownInterval);
                gameObject.countDownInterval = undefined;
                this.domManip.$id("game-countdown-image").style.display = "none";
            }
            endGameLoop();
            WebSocketManagerGame.disconnect(this.gameId)
            // Reset Game Object
            this.initObjects();
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