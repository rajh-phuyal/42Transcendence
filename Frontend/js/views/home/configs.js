import { audioPlayer } from '../../abstracts/audio.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import $store from '../../store/store.js';

export default {
    attributes: {
    },

    methods: {
        /* This function sets/unsets the atrributes so that the modals can get the data */
        setViewAttributes(set) {
            const view = this.domManip.$id("router-view");
            if(set) {
                // Set the attributes
                view.setAttribute("data-user-id", $store.fromState("user").id);
            } else {
                // Unset the attributes
                view.removeAttribute("data-user-id");
            }
        }
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            this.domManip.$off(window, "select-user-invite", this.selectUserToInvite);
            // Close the modal properly using Bootstrap's modal API before leaving
            const tournamentModal = bootstrap.Modal.getInstance(this.domManip.$id("home-modal"));
            if (tournamentModal) {
                tournamentModal.hide();
            }
			const homeModal = this.domManip.$id("home-modal");
			if (homeModal)
				homeModal.classList.add("custom-modal");

            this.domManip.$off(document, "click", mouseClick);
            this.domManip.$off(document, "mousemove", isHovering);
            this.setViewAttributes(false);
        },

        beforeDomInsertion() {
        },

        async afterDomInsertion() {
            // Start music
            audioPlayer.playMusic("home");
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = this.domManip.$id("home-canvas");
            canvasData.context = canvasData.canvas.getContext('2d');
            canvasData.canvas.width = 2000;
            canvasData.canvas.height = 900;
            canvasData.context.imageSmoothingEnabled = true;

            // build thexport e first frame
            await buildCanvas();

            // this.domManip.$on(document, "click", mouseClick);
            // this.domManip.$on(document, "mousemove", isHovering);
            EventListenerManager.linkEventListener("home-canvas", "home", "click", mouseClick);
            EventListenerManager.linkEventListener("home-canvas", "home", "mousemove", isHovering);
            // Set the attributes for the modals
            this.setViewAttributes(true);
        },
    }
}