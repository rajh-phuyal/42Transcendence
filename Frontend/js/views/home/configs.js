import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'
import call from '../../abstracts/call.js'
import callToast from '../../abstracts/callToast.js'
import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {
    },

    methods: {


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
			this.domManip.$off(this.domManip.$id('home-view'), "keydown", this.escapeCallback);
            let element = this.domManip.$id("modal-tournament-create-form-create-button");
            if (element)
                this.domManip.$off(element, "click", this.createTournament);

            element = this.domManip.$class("modal-tournament-create-maps-button");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            element = this.domManip.$class("modal-tournament-create-form-type-buttons");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            this.domManip.$off(this.domManip.$id("modal-tournament-create-form-join-button"), "click", this.toggleCreateJoinView);
            this.domManip.$off(this.domManip.$id("modal-tournament-join-form-host-button"), "click", this.toggleCreateJoinView);
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = this.domManip.$id("home-canvas");
            let canvas = canvasData.canvas;

            canvasData.context = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            // Adjust the pixel ratio so it draws the images with higher resolution
            const scale = window.devicePixelRatio;

            canvasData.context.imageSmoothingEnabled = true;
            canvasData.context.scale(scale, scale);

            // build thexport e first frame
            buildCanvas();

			const homeView = this.domManip.$id('home-view');
			this.domManip.$on(homeView, "keydown", this.escapeCallback);

            // for (let element of this.users)
                // this.createInviteUserCard(element);

            this.domManip.$on(document, "click", mouseClick);
            this.domManip.$on(document, "mousemove", isHovering);

            // Link "open Modal" to Buttons
            modalManager.on("modal-tournament-create-form-create-button", "modal-tournament");

            // OLD:
            //let element = this.domManip.$id("modal-tournament-create-form-create-button");
            //this.domManip.$on(element, "click", this.createTournament);

        },
    }
}