import { translate } from '../../locale/locale.js';
import router from '../../navigation/router.js';

export default {
    attributes: {

    },

    methods: {
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            // TODO: remove listener
        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            // Translate the page
            if (this.routeParams.msg)
                this.domManip.$id("404-title").innerText = this.routeParams.msg;
            else
                this.domManip.$id("404-title").innerText = translate("404", "title");
            let homeButton = this.domManip.$id("home-button");
            console.log("homebutton:",homeButton);
            // TODO: @rajh is this the correct way to translate the button?
            homeButton.name = translate("404", "homeButton");
            homeButton.render();
            this.domManip.$on(homeButton, "click", () => router("/"));
        },
    }
}