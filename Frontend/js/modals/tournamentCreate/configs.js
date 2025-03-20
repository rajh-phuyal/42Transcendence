import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {
        public: true,
        local: false,
        map: null,
        powerups: true,
    },

    methods: {
        selectPrivacy() {
            const privImgPublic     = this.domManip.$id("modal-tournament-create-priv-public");
            const privImgPrivate    = this.domManip.$id("modal-tournament-create-priv-private");
            const enabled = "modal-toggle-button-enabled";
            const disabled = "modal-toggle-button-disabled";
            if(this.public) {
                this.domManip.$removeClass(privImgPublic, disabled);
                this.domManip.$addClass(privImgPublic, enabled);
                this.domManip.$removeClass(privImgPrivate, enabled);
                this.domManip.$addClass(privImgPrivate, disabled);
            } else {
                this.domManip.$removeClass(privImgPublic, enabled);
                this.domManip.$addClass(privImgPublic, disabled);
                this.domManip.$removeClass(privImgPrivate, disabled);
                this.domManip.$addClass(privImgPrivate, enabled);
            }
        },
        selectType() {
            const typeLocal  = this.domManip.$id("modal-tournament-create-type-local");
            const typeRemote = this.domManip.$id("modal-tournament-create-type-remote");
            const enabled = "modal-toggle-button-enabled";
            const disabled = "modal-toggle-button-disabled";
            if(this.type === "local") {
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
        },
        selectPowerups() {
            const btn = this.domManip.$id("modal-tournament-btn-pu");
            if(this.powerups) {
                this.domManip.$addClass(btn, "modal-toggle-button-disabled");
                this.domManip.$removeClass(btn, "modal-toggle-button-enabled");
            }
            else {
                btn.classList.remove("modal-toggle-button-disabled");
                btn.classList.add("modal-toggle-button-enabled");
            }
        },

        callbackSelectPrivacy(event) {
            const value = event.srcElement.attributes.datapublic.value;
            this.public = value === "true";
            this.selectPrivacy();
        },
        callbackSelectType(event) {
            this.type = event.srcElement.attributes.datatype.value;
            this.selectType();
        },
        callbackSelectMap(event) {
            this.map = parseInt(event.srcElement.attributes.mapid.value);
            this.selectMap();
        },
        callbackPowerups(event) {
            this.powerups = !this.powerups;
            this.selectPowerups();
        },
    },

    hooks: {
        beforeOpen () {
            // Init the toogle images
            // - Chosse a random map if not set
            if (!this.map) {
                this.map = Math.floor(Math.random() * 4) + 1;
                this.selectMap();
            }
            this.selectPrivacy();
            this.selectType();

            // Add event listeners
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
        },

        afterClose () {
        }
    }
}