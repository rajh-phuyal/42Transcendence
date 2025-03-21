import {imageBook, backgroundImageBook, labels, lines} from './objects.js'
import canvasData from './data.js'
import { $id } from '../../abstracts/dollars.js';

/*
*************************************************************
******************* DRAWING FUNCTIONS ***********************
*************************************************************
*/

// Draw the image on the canvas
function drawImg(image) {
    canvasData.image = image;
    return new Promise((resolve) => {
        let imageObject = new Image();
        let image = canvasData.image;

        imageObject.src = image.src;

        imageObject.onload = function () {
            let context = canvasData.context;
            let shadowColor;
            let image = canvasData.image;

        // Draw the image on the canvas once it's loaded
            if (image.highleted)
                shadowColor = '#FFFCE6'
            else
                shadowColor = '#100C09';

            context.shadowColor = shadowColor;
            context.shadowOffsetX = image.shadow;
            context.shadowOffsetY = image.shadow;
            context.drawImage(imageObject, image.x, image.y, image.width, image.height);

            context.shadowColor = shadowColor;
            context.shadowOffsetX = -image.shadow;
            context.shadowOffsetY = -image.shadow;

            context.drawImage(imageObject, image.x, image.y, image.width, image.height);

            // Reset shadow offsets
            context.shadowOffsetX = 0;
            context.shadowOffsetY = 0;

            resolve();
        };

        imageObject.onerror = function () {
            console.error("Error loading image:", image.src);
            resolve();
        };
    });
}

// draw the imageBook
async function drawImageBook(){
    for (const element of imageBook)
       await drawImg(element);
}

// draw the label in the canvas
function drawLabel(label){

    let context = canvasData.context;

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

    let context = canvasData.context;

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
        await drawImg(element);

    for (const element of labels)
        drawLabel(element);

    for (const element of lines)
        drawLine(element);
}

async function redraw(image)
{
    await drawImg(image);
    for (let element of image.lines)
    {
        drawLine(lines[element]);
    }

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
export async function isHovering(event){

    // This should prevent the background to respond if a modal is open
    if (document.querySelectorAll('.modal.show').length > 0)
        return ;

    let canvas = canvasData.canvas;

    // get the canvas position relative to the viewport
    const rect = canvas.getBoundingClientRect();

    // Adjust the mouse position relative to the canvas
    let mouseX = (event.clientX - rect.left) * (canvas.width / canvas.clientWidth);
    let mouseY = (event.clientY - rect.top) * (canvas.height / canvas.clientHeight);

    // the state variable stores the id of the element currently highlighted
    let state = canvasData.highlitedImageID;

    let foundElement = imageBook.find(element => isContained(mouseX, mouseY, element));

    if ((!foundElement && state == 0) || (foundElement && foundElement.id == state))
        return ;

    if (foundElement)
        foundElement.highleted = true;


    for (const element of imageBook) {
        if (element !== foundElement) {
            if (element.highleted) {
                element.highleted = false;
                await redraw(element);
            }
        }
    }

    if (foundElement == undefined)
    {
        canvasData.highlitedImageID = 0;
        return ;
    }

    canvasData.highlitedImageID = foundElement.id;
    await redraw(foundElement);
}

// deals with the clicking events
export function mouseClick(event){

    // This should prevent the background to respond if a modal is open
    if (document.querySelectorAll('.modal.show').length > 0)
        return ;

	let mouseX = event.clientX;
    let mouseY = event.clientY;

    let foundElement = imageBook.find(element => isContained(mouseX, mouseY, element));

    if (!foundElement)
        foundElement = backgroundImageBook.find(element => isContained(mouseX, mouseY, element));
    else
        foundElement.callback();

    if (!foundElement)
        return ;
}