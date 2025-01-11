import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'

export default {
    attributes: {
    },

    methods: {

        createTournament() {
            const tournamentName = this.domManip.$id("tournament-modal-create-form-name-container-input").value;
            const powerups = this.domManip.$id("tournament-modal-create-form-name-container-checkbox").checked;
            console.log(tournamentName, powerups);

            
            
        },
		toggleCreateJoinView() {
			const createTournament = $id("tournament-modal-create-container");
			const joinTournament = $id("tournament-modal-join-container");
			const displaySwitch = {
				flex: "none",
				none: "flex"
			};
			createTournament.style.display = displaySwitch[window.getComputedStyle(createTournament, null).display];
			joinTournament.style.display = displaySwitch[window.getComputedStyle(joinTournament, null).display];
		}
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            $off(document, "click", mouseClick);
            $off(document, "mousemove", isHovering);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            this.domManip.$off(element, "click", this.createTournament);
            this.domManip.$off(element, "click", this.toggleCreateJoinView);
        },

        beforeDomInsertion() {
            
        },

        afterDomInsertion() {
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = $id("home-canvas");
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

            $on(document, "click", mouseClick);
            $on(document, "mousemove", isHovering);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            this.domManip.$on(element, "click", this.createTournament);
			this.domManip.$on(this.domManip.$id("tournament-modal-create-form-join-button"), "click", this.toggleCreateJoinView);
			this.domManip.$on(this.domManip.$id("tournament-modal-join-form-host-button"), "click", this.toggleCreateJoinView);
        },
    }
}