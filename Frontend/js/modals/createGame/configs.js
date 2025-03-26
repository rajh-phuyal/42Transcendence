import $callToast from '../../abstracts/callToast.js';
import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        isOpponentFixed: true,
        opponentId: null,
        avatar: null,
        username: null,

        backgrounds: {
            1: "../../assets/backgrounds/modal-create-game-ufo.png",
            2: "../../assets/backgrounds/modal-create-game-lizard-people.png",
            3: "../../assets/backgrounds/modal-create-game-snowman.png",
            4: "../../assets/backgrounds/modal-create-game-lochness.png",
        },

        map: null,
        powerups: true,
    },

    methods: {
        translateElements() {
            this.domManip.$id("modal-create-game-opponent-search").title = translate("createGame", "placeholderSearchbar");
        },

        /* This functions toggles between selecting a user and fixing it */
        updateOpponentSection() {
            const search = this.domManip.$id("modal-create-game-opponent-search");
            const username = this.domManip.$id("modal-create-game-opponent-username");
            const avatar = this.domManip.$id("modal-create-game-opponent-avatar");

            /* Greyout the search if fixed opponent*/
            if (this.isOpponentFixed)
                search.style.display = "none";
            else
                search.style.display = "block";

            /* Show the opponent info if availiable*/
            if (this.username) {
                username.textContent = this.username;
                username.style.display = "block";
            } else {
                username.textContent = "";
                username.style.display = "none";
            }
            if (this.avatar) {
                avatar.src = window.origin + '/media/avatars/' + this.avatar;
                avatar.style.display = "block";
            } else {
                avatar.src = "";
                avatar.style.display = "none";
            }
        },

        callbackSearchbar(event) {
            const user = event.detail.user;
            // console.log(user);
            this.opponentId = user.id;
            this.avatar = user.avatar;
            this.username = user.username;
            // console.log(this.opponentId, this.avatar, this.username);
            this.updateOpponentSection();
        },

        callbackPowerups(event) {
            const btn = this.domManip.$id("modal-create-game-btn-pu");
            if(this.powerups) {
                this.powerups = false;
                this.domManip.$addClass(btn, "modal-toggle-button-disabled");
                this.domManip.$removeClass(btn, "modal-toggle-button-enabled");
            }
            else {
                this.powerups = true;
                btn.classList.remove("modal-toggle-button-disabled");
                btn.classList.add("modal-toggle-button-enabled");
            }
            // Deactive the button for asthetics
            event.srcElement.blur();
        },

        callbackSelectMap(event) {
            this.map = parseInt(event.srcElement.attributes.mapid.value);
            this.selectMap();
        },

        selectMap() {
            // Loop trough all maps and select the one that is clicked by adding the class enabled
            const mapImgs = this.domManip.$class("map-button");
            for (let mapImg of mapImgs) {
                if (mapImg.attributes.mapid.value == this.map) {
                    mapImg.classList.remove("modal-toggle-button-disabled");
                    mapImg.classList.add("modal-toggle-button-enabled");
                } else {
                    mapImg.classList.remove("modal-toggle-button-enabled");
                    mapImg.classList.add("modal-toggle-button-disabled");
                }
            }
            // Change the background image
            const backgroundImg = this.domManip.$id("modal-create-game-background");
            backgroundImg.src = this.backgrounds[this.map];
        },

        createGame() {
            if (!this.opponentId) {
                $callToast("error", translate("createGame", "selectOpponent"));
                return;
            }
            if(!this.map) {
                $callToast("error", translate("createGame", "selectMap"));
                return;
            }
            const data = {
                "mapNumber": this.map,
                "powerups": this.powerups,
                "opponentId": this.opponentId,
            }
            call('game/create/', 'POST', data).then(data => {
                router('/game', {"id": data.gameId});
            })
        },
    },

    hooks: {
        /*
        This function is called before opening the modal to check if the modal should be opened or not
        In this case: if a game already exists: don't open modal but redir to game
        */
        async allowedToOpen() {
            let checkIsOpponentFixed = false;
            let checkOpponentId = undefined;
            try {
                // Try to store userId (wich is the opponent) as Number
                checkOpponentId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
                if(checkOpponentId)
                    checkIsOpponentFixed = true;
            } catch (error) {
                console.error("Error in allowedToOpen: ", error);
            }
            // Check if the user is already in a game -> redir to game
            if (checkIsOpponentFixed) {
                try {
                    let data = await call(`game/get-game/${checkOpponentId}/`, 'GET');
                    if (data.gameId) {
                        router('/game', {"id": data.gameId});
                        return false;
                    }
                } catch (error) {
                    console.error("Error in call game/get-game");
                    return false;
                }
            }
            return true;
        },
        async beforeOpen () {
            this.translateElements();

            // Fetching the attributes from view and store them locally
            this.isOpponentFixed = false;
            try {
                // Try to store userId (wich is the opponent) as Number
                this.opponentId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
                if(this.opponentId)
                    this.isOpponentFixed = true;
            } catch (error) {}
            this.avatar = this.domManip.$id("router-view").getAttribute("data-user-avatar");
            this.username = this.domManip.$id("router-view").getAttribute("data-user-username");
            if (this.isOpponentFixed && (!this.avatar || !this.username))
                console.error("createGameModal: Couldn't find the avatar or username attribute in the view");

            // Chosse a random map if not set
            if (!this.map) {
                this.map = Math.floor(Math.random() * 4) + 1;
                this.selectMap();
            }

            // Add event listener
            this.domManip.$on(this.domManip.$id("modal-create-game-btn-pu"), "click", this.callbackPowerups);
            this.domManip.$on(this.domManip.$id("modal-create-game-map-ufo"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-create-game-map-lizard-people"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-create-game-map-snowman"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-create-game-map-lochness"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-create-game-btn-create"), "click", this.createGame);
            // For search bar
            this.domManip.$on(window, "modal-create-game-select-user", this.callbackSearchbar);

            this.updateOpponentSection();
        },

        afterClose () {
            // Remove event listener
            this.domManip.$off(this.domManip.$id("modal-create-game-btn-pu"), "click", this.callbackPowerups);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-ufo"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-lizard-people"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-snowman"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-lochness"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-btn-create"), "click", this.createGame);
            this.domManip.$off(window, "modal-create-game-select-user", this.callbackSearchbar);
        }
    }
}