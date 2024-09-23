import { $id, $on, $off } from '../../abstracts/dollars.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'

export default {
    attributes: {
    },
    
    methods: {
    },
    
    hooks: {
        beforeRouteEnter() {

        },
        
        beforeRouteLeave() {
            $off(document, "click", mouseClick);
            $off(document, "mousemove", isHovering);
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
        },
    }
}