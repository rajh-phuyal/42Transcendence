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
            
            // state of the mouse => if its hovering an image (= 0) or not (> 0), and if it is, which one (its indicated by the imageBook.id)
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