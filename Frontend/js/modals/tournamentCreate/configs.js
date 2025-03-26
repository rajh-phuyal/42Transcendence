import { generateTournamentName } from './generateName.js';
import call from '../../abstracts/call.js'
import callToast from '../../abstracts/callToast.js'
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        public: true,
        local: false,
        map: Math.floor(Math.random() * 4) + 1,
        powerups: true,
        opponentIds: [],
    },

    methods: {
        translateElements() {
            this.domManip.$id("modal-tournament-tournament-title").setAttribute("placeholder", translate("tournamentCreate", "placeholderName"));
            this.domManip.$id("modal-tournament-opponents-content").title = translate("tournamentCreate", "placeholderInviteUser");
        },

        updatePrivacy() {
            const privImgPublic     = this.domManip.$id("modal-tournament-create-priv-public");
            const privImgPrivate    = this.domManip.$id("modal-tournament-create-priv-private");
            const enabled = "modal-toggle-button-enabled";
            const disabled = "modal-toggle-button-disabled";
            if(this.public) {
                this.domManip.$removeClass(privImgPublic, disabled);
                this.domManip.$addClass(privImgPublic, enabled);
                this.domManip.$removeClass(privImgPrivate, enabled);
                this.domManip.$addClass(privImgPrivate, disabled);
                // Hide the select opponent area
                console.warn(this.domManip.$id("modal-tournament-opponents-header"));
                this.domManip.$id("modal-tournament-opponents-header").style.display = "none";
                this.domManip.$id("modal-tournament-opponents-content").style.display = "none";
            } else {
                this.domManip.$removeClass(privImgPublic, enabled);
                this.domManip.$addClass(privImgPublic, disabled);
                this.domManip.$removeClass(privImgPrivate, disabled);
                this.domManip.$addClass(privImgPrivate, enabled);
                // Show the select opponent area
                this.domManip.$id("modal-tournament-opponents-header").style.display = "block";
                this.domManip.$id("modal-tournament-opponents-content").style.display = "block";
            }
        },
        updateType() {
            const typeLocal  = this.domManip.$id("modal-tournament-create-type-local");
            const typeRemote = this.domManip.$id("modal-tournament-create-type-remote");
            const enabled = "modal-toggle-button-enabled";
            const disabled = "modal-toggle-button-disabled";
            if(this.local) {
                this.domManip.$removeClass(typeLocal, disabled);
                this.domManip.$addClass(typeLocal, enabled);
                this.domManip.$removeClass(typeRemote, enabled);
                this.domManip.$addClass(typeRemote, disabled);
            } else {
                this.domManip.$removeClass(typeLocal, enabled);
                this.domManip.$addClass(typeLocal, disabled);
                this.domManip.$removeClass(typeRemote, disabled);
                this.domManip.$addClass(typeRemote, enabled);
            }
        },
        updateMap() {
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
        },
        updatePowerups() {
            const btn = this.domManip.$id("modal-tournament-btn-pu");
            if(this.powerups) {
                this.domManip.$removeClass(btn, "modal-toggle-button-disabled");
                this.domManip.$addClass(btn, "modal-toggle-button-enabled");
                btn.innerHTML = translate("tournamentCreate", "enabled");
            }
            else {
                this.domManip.$addClass(btn, "modal-toggle-button-disabled");
                this.domManip.$removeClass(btn, "modal-toggle-button-enabled");
                btn.innerHTML = translate("tournamentCreate", "disabled");
            }
        },
        updateOpponents() {
            const opponentListContainer = this.domManip.$id("modal-tournament-create-opponents-container");
            opponentListContainer.innerHTML = "";
            if (this.opponentIds.length === 0) {
                opponentListContainer.innerHTML = `<h6 style='color: black; padding 5px;'>${translate("tournamentCreate", "noOpponents")}</h6>`;
                return;
            }
            for (let opponent of this.opponentIds) {
                let template = this.domManip.$id("modal-tournament-create-opponent-template").content.cloneNode(true);
                const container = template.querySelector(".modal-tournament-create-opponent-container");
                // Set the user id
                container.setAttribute("opponent-id", opponent.id);
                template.querySelector(".modal-tournament-create-opponent-avatar").src = window.location.origin + "/media/avatars/" + opponent.avatar;
                template.querySelector(".modal-tournament-create-opponent-username").textContent = opponent.username;
                this.domManip.$on(template.querySelector(".modal-tournament-create-btn-delete-opponent"), "click", this.callBackDeleteOpponentCard);
                opponentListContainer.appendChild(container);
            }
        },

        callbackSelectPrivacy(event) {
            const value = event.srcElement.attributes.datapublic.value;
            this.public = value === "true";
            this.updatePrivacy();
        },
        callbackSelectType(event) {
            const value = event.srcElement.attributes.datalocal.value;
            this.local = value === "true";
            this.updateType();
        },
        callbackSelectMap(event) {
            this.map = parseInt(event.srcElement.attributes.mapid.value);
            this.updateMap();
        },
        callbackPowerups(event) {
            // Deactive the button for asthetics
            event.srcElement.blur();
            this.powerups = !this.powerups;
            this.updatePowerups();
        },
        callbackGenerateName() {
            this.domManip.$id("modal-tournament-tournament-title").value = generateTournamentName();
        },
        callbackSelectUser(event) {
            const user = event.detail.user;
            // Only add user if he doesnt exist already
            if (!this.opponentIds.some(opponent => opponent.id === user.id)) {
                this.opponentIds.push(user);
                this.updateOpponents();
            }
        },
        callBackDeleteOpponentCard(event) {
            const opponentCard = event.srcElement.parentElement;
            const clickedId = parseInt(opponentCard.attributes["opponent-id"].value);
            // Remove it from the stored ids
            this.opponentIds = this.opponentIds.filter(opponent => opponent.id !== clickedId);
            // Delete the card
            opponentCard.remove();
            // If list empty add the message by calling:
            if(this.opponentIds.length === 0)
                this.updateOpponents();
        },
        callbackCreateTournament() {
            this.domManip.$id("modal-tournament-tournament-title").value = this.domManip.$id("modal-tournament-tournament-title").value.trim();
            const tournamentName = this.domManip.$id("modal-tournament-tournament-title").value.trim();
            // For public tournaments remove the opponents
            if(this.public)
                this.opponentIds = [];
            call('tournament/create/', "POST", {
                "name":             tournamentName,
                "public":           this.public,
                "local":            this.local,
                "mapNumber":        this.map,
                "powerups":         this.powerups,
                "opponentIds":      this.opponentIds.map(opponent => opponent.id),
            }).then(data => {
                callToast("success", data.message);
                this.router(`/tournament`, { id: data.tournamentId });
            }).catch(error => {
                callToast("error", error.message);
            });
        },
    },

    hooks: {
        beforeOpen () {
            this.translateElements();
            // Init the toogle images
            this.updateMap();
            this.updatePrivacy();
            this.updateType();
            this.updateOpponents();
            this.updatePowerups();
            // Set a random name
            this.callbackGenerateName();
            // Add event listeners
            // - TITLE GENERATOR
            this.domManip.$on(this.domManip.$id("modal-tournament-btn-title-gen"), "click", this.callbackGenerateName);
            // - PRIVACY
            this.domManip.$on(this.domManip.$id("modal-tournament-create-priv-public"), "click", this.callbackSelectPrivacy);
            this.domManip.$on(this.domManip.$id("modal-tournament-create-priv-private"), "click", this.callbackSelectPrivacy);
            // - TYPE
            this.domManip.$on(this.domManip.$id("modal-tournament-create-type-local"), "click", this.callbackSelectType);
            this.domManip.$on(this.domManip.$id("modal-tournament-create-type-remote"), "click", this.callbackSelectType);
            // - MAPS
            this.domManip.$on(this.domManip.$id("modal-tournament-create-map-ufo"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-tournament-create-map-lizard-people"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-tournament-create-map-snowman"), "click", this.callbackSelectMap);
            this.domManip.$on(this.domManip.$id("modal-tournament-create-map-lochness"), "click", this.callbackSelectMap);
            // - POWERUPS
            this.domManip.$on(this.domManip.$id("modal-tournament-btn-pu"), "click", this.callbackPowerups);
            // - USER SELECT
            this.domManip.$on(window, "select-user-invite", this.callbackSelectUser);
            // - CREATE
            this.domManip.$on(this.domManip.$id("modal-tournament-create-btn-create"), "click", this.callbackCreateTournament);
        },

        afterClose () {
        }
    }
}