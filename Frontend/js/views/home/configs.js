import { $id, $on } from '../../abstracts/dollars.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'

export default {
    attributes: {
    },
    
    methods: {
    },
    
    hooks: {
        beforeRouteEnter() {
            console.log("step 1");
        },
        
        beforeRouteLeave() {
            console.log("step 2");
        },

        beforeDomInsertion() {
            console.log('store', this.$store);
            console.log("dstep 3");
        },

        afterDomInsertion() {
            console.log("step 4");
            
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = $id("home-canvas");
            let canvas = canvasData.canvas;
            console.log(canvas);
            canvasData.context = canvas.getContext('2d');

            // Adjust the pixel ratio so it draws the images with higher resolution
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            const scale = window.devicePixelRatio;

            // Adjusts the canvas size
            canvas.width = canvas.clientWidth * scale;
            canvas.height = canvas.clientHeight * scale;

            canvasData.context.imageSmoothingEnabled = true;
            canvasData.context.scale(scale, scale);

            // build thexport e first frame
            buildCanvas();

            $on(document, "click", mouseClick);
            $on(document, "mousemove", isHovering);
        },
    }
}