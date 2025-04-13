import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import { translate } from '../../locale/locale.js';
import router from '../../navigation/router.js';
import { audioPlayer } from '../../abstracts/audio.js';

export default {
    attributes: {
    },

    methods: {
        buttonCallback() {
            router("/");
        },
        keydownCallback(event) {
            if (event.key === "Enter" || event.key === " " || event.key === "Escape")
                this.buttonCallback();
        },
    },

    hooks: {
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            audioPlayer.playMusic("404");
            if (this.routeParams && this.routeParams.msg)
                this.domManip.$id("404-title").innerText = "404 | "+ this.routeParams.msg;
            else
                this.domManip.$id("404-title").innerText = translate("404", "title");
            EventListenerManager.linkEventListener("home-button", "404", "click", this.buttonCallback);
            // FUTURE: This is a nice idea but atm this listener is not removed so the esc still works after leaving the view - if time need to reserach why
            // EventListenerManager.linkEventListener("barely-a-body", "404", "keydown", this.keydownCallback);
        },
    }
}