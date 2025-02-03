import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';
import { endGameLoop, changeGameState } from './methods.js';
import { gameRender } from './render.js';
import { gameObject } from './objects.js';

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

                    // Set game data
                    gameObject.playerLeft.points = data.playerLeft.points;
                    gameObject.playerRight.points = data.playerRight.points;
                    this.map = this.maps[data.gameData.mapNumber];

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

            gameObject.playerLeft.powerups.big = "used";  // active / used / available
            gameObject.playerRight.powerups.big = "used";
            gameObject.playerLeft.powerups.slow = "used";
            gameObject.playerRight.powerups.slow = "used";
            gameObject.playerLeft.powerups.fast = "used";
            gameObject.playerRight.powerups.fast = "used";
        },
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
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
            await this.loadDetails()

			const gameField = this.domManip.$id("game-field");
			const ctx = gameField.getContext('2d');
			ctx.clearRect(0, 0, gameField.width, gameField.height);

			gameRender(gameField, ctx);

            //TODO: I uncommented the button so that for debung we always see the game field
            // related to issue: #304
			//const goToGameButton = this.domManip.$id("go-to-game");
			//goToGameButton.addEventListener('click', () => {
				const gameViewImageContainer = this.domManip.$id("game-view-image-container");
				const gameImageContainer = this.domManip.$id("game-view-map-image");
				const gameImage = gameImageContainer.children[0];
				gameField.style.display = "block";
				gameImage.src = window.location.origin + '/assets/game/maps/lizard-people.png';
				gameViewImageContainer.style.backgroundImage = "none";
				gameViewImageContainer.style.width= "100%";
				gameImage.style.display = "block";
			//});
		},
    }
}