import imageBook from './objects.js'
import backgroundImageBook from './objects.js'
import labels from './objects.js'
import lines from './objects.js'
import $store from '../../store/store.js'

console.log("here");

/* 
*************************************************************
******************* DRAWING FUNCTIONS ***********************
*************************************************************
*/

// Draw the image on the canvas
function drawImg(image, color) {
    return new Promise((resolve) => {
        let imgageObject = new Image();
        let shadowColor;

        imgageObject.src = image.src;
        
        if (color)
            shadowColor = color;
        else
            shadowColor = '#100C09';
        
        imgageObject.onload = function () {
            // Draw the image on the canvas once it's loaded
            context.shadowColor = shadowColor;
            context.shadowOffsetX = image.shadow;
            context.shadowOffsetY = image.shadow;
            
            context.drawImage(imgageObject, image.x, image.y, image.width, image.height);
            
            context.shadowColor = shadowColor;
            context.shadowOffsetX = -image.shadow;
            context.shadowOffsetY = -image.shadow;
            
            context.drawImage(imgageObject, image.x, image.y, image.width, image.height);
            
            // Reset shadow offsets
            context.shadowOffsetX = 0;
            context.shadowOffsetY = 0;
            
            // Resolve the promise after drawing is complete
            resolve();
        };

        imgageObject.onerror = function () {
            console.error("Error loading image:", image.src);
            resolve();  // Resolve even on error to avoid blocking
        };
    });
}

// draw the imageBook
async function drawImageBook(){
    for (let i = 0; i < imageBook.length; i++)
       await drawImg(imageBook[i], undefined);
}

// draw the label in the canvas
function drawLabel(label){
    
    // Draw the rectangle
    context.beginPath();
    context.rect(label.x, label.y, label.width, label.height);
    context.fillStyle = '#FFF6D4';
    context.strokeStyle = 'black';
    context.lineWidth = 3;
    context.fill();
    context.stroke();

    // draw the text
    context.fillStyle = 'black';
    context.font = "bold 16px Chalkduster";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(label.text, label.x + (label.width / 2), label.y + (label.height / 2))
    context.closePath();

    
}

// draw a line in the canvas
function drawLine(line){

    context.beginPath();
    context.strokeStyle = '#D32929';
    context.lineWidth = 3;
    context.moveTo(line.x1, line.y1);
    context.lineTo(line.x2, line.y2);
    context.stroke();
    context.closePath();
    context.beginPath();
    context.fillStyle = '#3D3D3D'
    context.arc(line.x1, line.y1, 5, 0, 2 * Math.PI);
    context.arc(line.x2, line.y2, 5, 0, 2 * Math.PI);
    context.fill()
    context.closePath();
}

// build the whole canvas
export async function buildCanvas(){
    await drawImageBook();
    for (const element of backgroundImageBook)
        await drawImg(element, undefined);

    for (const element of labels)
        drawLabel(element);
    
    for (const element of lines)
        drawLine(element);
}

async function redraw(image, color)
{
    if (image == undefined)
        return;
    await drawImg(image, color);
    for (element of image.lines)
        drawLine(lines[element]);

}

/* 
************************************************************
************************ EVENTS ****************************
************************************************************
*/
   
// check if the mouse mouse coordinates match the images for the imageBook
function isContained(x, y, img){
    return (x >= img.x && x <= (img.x + img.width) && y >= img.y && y <= (img.y + img.height))
}


// deals with the hovering events
export function isHovering(event){

    let mouseX = event.clientX;
    let mouseY = event.clientY;
    
    let state = $store.state.homeViewUImageState;

    foundElement = imageBook.find(element => isContained(mouseX, mouseY, element));
    
    if ((!foundElement && state == 0) || (foundElement && foundElement.id == state))
        return ;
    
    if (state)
        redraw(imageBook[state - 1], '#100C09');
    
    if (foundElement){
        redraw(foundElement, '#FFFCE6');
        $store.commit("setHomeViewUImageState", foundElement.id);
    }
    else
        $store.commit("setHomeViewUImageState", 0);
}

// deals with the clicking events
export function mouseClick(event){
    
    lines.forEach(element => {
        drawLine(element);
    });
    
    mouseX = event.clientX;
    mouseY = event.clientY;
    
    foundElement = imageBook.find(element => isContained(mouseX, mouseY, element));

    if (!foundElement)
        foundElement = backgroundImageBook.find(element => isContained(mouseX, mouseY, element));
    
    
    if (!foundElement){
        console.log("offbounds");
        return;
    }

    console.log('=========================');
    console.log('element src:', foundElement.src);
    console.log('mouse position:', mouseX, mouseY);
    
}

/* 
*************************************************************
************************* SETUP *****************************
*************************************************************
*/

// state of the mouse => if its hovering an image (= 0) or not (> 0), and if it is, which one (its indicated by the imageBook.id)
// state = 0;

// // Get the canvas element and its context
// canvas = document.getElementById('canvas');
// console.log(canvas);
// context = canvas.getContext('2d');

// // Adjust the pixel ratio so it draws the images with higher resolution
// canvas.width = window.innerWidth;
// canvas.height = window.innerHeight;

// const scale = window.devicePixelRatio;

// canvas.width = canvas.clientWidth * scale;
// canvas.height = canvas.clientHeight * scale;

// context.imageSmoothingEnabled = true;
// context.scale(scale, scale);

// build thexport e first frame
buildCanvas();

// event listeners
// document.addEventListener("mousemove", isHovering);
// document.addEventListener("click", mouseClick);

