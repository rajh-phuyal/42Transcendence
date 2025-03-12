/*
TODO: THIS MODAL IS NOT DONE AT ALL!!!
    NEED TO:
        - copy the right structure from the template modal
        - double check all nodes/elements if needed?
        - adjust the js code
            - move it from original configs.js (profile/home) to congigs.js of modal!
            - make sure the js code has all values. the idea is that the view stores the info as attribute and the modal takes it from there
            - e.g. newConversation modal js!
*/


import { modalManager } from '../../abstracts/ModalManager.js';
import $callToast from '../../abstracts/callToast.js';
import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';

export default {
    attributes: {
        opponentId: null,
        avatar: null,
        username: null,

/*         //TODO: place this map in the store
        maps: {
            "ufo": 1,
            "lizard-people": 2,
            "snowman": 3,
            "lochness": 4,
        },
 */
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
        callbackPowerups(event) {
            console.log("powerups");
            const btn = this.domManip.$id("modal-create-game-btn-pu");
            if(this.powerups) {
                console.log("powerups false");
                this.powerups = false;
                this.domManip.$addClass(btn, "modal-toggle-button-disabled");
                this.domManip.$removeClass(btn, "modal-toggle-button-enabled");
                console.log("powerups false-DONE");
            }
            else {
                console.log("powerups true");
                this.powerups = true;
                btn.classList.remove("modal-toggle-button-disabled");
                btn.classList.add("modal-toggle-button-enabled");
            }
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
            console.log(this.map);
            backgroundImg.src = this.backgrounds[this.map];
            console.log(backgroundImg.src);
        },

        createGame() {
            /* TODO: This section needs translations!! */
            if (!this.opponentId) {
                $callToast("error", "U need to select an opponent first");
                return;
            }
            if(!this.map) {
                $callToast("error", "U need to select a map first");
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
        async beforeOpen () {
            console.log("beforeOpen of modal-create-game");

            // Fetching the attributes from view and store them locally
            try {
                // Try to store userId (wich is the opponent) as Number
                this.opponentId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
            } catch {
                console.error("createGameModal: Couldn't find the opponentId ('data-user-id') attribute in the view");
                return false;
            }
            if (!this.opponentId) {
                console.error("createGameModal: Couldn't find the opponentId ('data-user-id') attribute in the view");
                return false;
            }
            this.avatar = this.domManip.$id("router-view").getAttribute("data-user-avatar");
            this.username = this.domManip.$id("router-view").getAttribute("data-user-username");
            if (!this.avatar || !this.username) {
                console.error("createGameModal: Couldn't find the avatar or username attribute in the view");
                return false;
            }

            // Check if the user is already in a game -> redir to game
            try {
                let data = await call(`game/get-game/${this.opponentId}/`, 'GET');
                if (data.gameId) {
                    console.log("User is already in a game, redirecting to game");
                    router('/game', {"id": data.gameId});
                    return false;
                }
            } catch (error) {
                console.error("Error in call game/get-game");
                return false;
            }

            // Set modal title and opponent info
            this.domManip.$id("modal-create-game-title").textContent = "Create friendly match"; //Todo: translate
            this.domManip.$id("modal-create-game-opponent-avatar").src = window.origin + '/media/avatars/' + this.avatar;
            this.domManip.$id("modal-create-game-opponent-username").textContent = this.username;

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
            return true;
        },
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            // Remove event listener
            this.domManip.$off(this.domManip.$id("modal-create-game-btn-pu"), "click", this.callbackPowerups);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-ufo"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-lizard-people"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-snowman"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-map-lochness"), "click", this.callbackSelectMap);
            this.domManip.$off(this.domManip.$id("modal-create-game-btn-create"), "click", this.createGame);
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {
        },
    }
}