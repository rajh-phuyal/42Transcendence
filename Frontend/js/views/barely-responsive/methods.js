import { $id } from '../../abstracts/dollars.js'

export function zoomIn(width, height) {

    let a = 1 - (width / 1020);
    let b = 1 - (height / 1020);
    // console.log("a: ", a, "b: ", b);
    let c = Math.max(Math.abs(a), Math.abs(b));
    let zoom = 1 + c;

    let imgElement = $id("overlord-denys-resize");
    // console.log("zoomIn", imgElement);
    if (imgElement){
        imgElement.style.transform = `scale(${zoom})`;
        // console.log("imgElement set to zoomn: ", zoom);
    }
        // console.log("imgElement is null");
}