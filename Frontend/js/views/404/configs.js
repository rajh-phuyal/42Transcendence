import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import { translate } from '../../locale/locale.js';
import router from '../../navigation/router.js';

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
            if (this.routeParams && this.routeParams.msg)
                this.domManip.$id("404-title").innerText = "404 | "+ this.routeParams.msg;
            else
                this.domManip.$id("404-title").innerText = translate("404", "title");
            let homeButton = this.domManip.$id("home-button");
            homeButton.innerText = translate("404", "homeButton");
            EventListenerManager.linkEventListener("home-button", "404", "click", this.buttonCallback);
            EventListenerManager.linkEventListener("barely-a-body", "404", "keydown", this.keydownCallback);
        },
    }
}