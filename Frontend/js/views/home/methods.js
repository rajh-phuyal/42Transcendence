import { $id } from '../../abstracts/dollars.js'
import canvasData from './data.js';
import { buildCanvas, redraw } from './script.js';

export async function rescaleCanvas(width, height)
    // TODO: NOT WORKING YET!
{
    let canvas = canvasData.canvas;
    canvasData.canvas = $id("home-canvas");
    canvasData.context = canvas.getContext('2d');
    const scale = window.devicePixelRatio;
    await canvasData.context.scale(window.innerWidth * scale, window.innerHeight * scale);
    await buildCanvas();

    /* let homeViewImage = $id('home-view-image'); */
    /* console.log("homeViewImage", homeViewImage.width, homeViewImage.height); */
    /* canvas.width = homeViewImage.width; */
    /* canvas.height = homeViewImage.height; */
    /* if (canvasData.image) */
    /*     await redraw(canvasData.image); */
    /* else */
    /*     await buildCanvas(); */
}


export function generateTournamentName() {
var list = [
"amazing", "great", "awesome", "fantastic", "incredible", "marvelous", "outstanding",
"spectacular", "brilliant", "superb", "legendary", "remarkable", "magnificent",
"extraordinary", "phenomenal", "glorious", "exceptional", "stunning", "breathtaking",
"impressive", "epic", "majestic", "radiant", "stupendous", "unbelievable", "unreal",
"supreme", "colossal", "splendid", "sensational", "mind-blowing", "electrifying",
"thrilling", "astonishing", "fabulous", "staggering", "miraculous", "delightful",
"euphoric", "flawless", "golden", "pristine", "divine", "top-tier", "elite", "dazzling",
"fearless", "resilient", "invincible", "unstoppable", "fearsome", "heroic", "victorious",
"unstoppable", "unshakable", "valiant", "bold", "daring", "mighty", "formidable", "courageous",
"indomitable", "fiery", "ferocious", "dominant", "glowing", "fierce", "radiant", "triumphant",
"fearless", "thunderous", "roaring", "unstoppable", "unyielding", "champion", "gallant", "noble",
"powerful", "energizing", "savage", "brave", "charismatic", "charming", "adventurous", "determined",
"unstoppable", "irresistible", "passionate", "exuberant", "vivacious", "zesty", "inspirational",
"uplifting", "graceful", "harmonious", "effervescent", "bouncy", "cheerful", "enthusiastic",
"spirited", "dynamic", "radiating", "persevering", "wholesome", "ecstatic", "enchanting",
"magical", "whimsical", "splendiferous", "proud", "jubilant", "cheery", "luminous", "joyful",
"grateful", "sunny", "buoyant", "optimistic", "hopeful", "elated", "elevated", "jolly", "exhilarating",
"exultant", "serene", "heavenly", "vibrant", "limitless", "boundless", "sky-high", "high-spirited",
"resplendent", "chivalrous", "shining", "resurgent", "illustrious", "pure", "radiance", "sparkling",
"futuristic", "trailblazing", "visionary", "ahead", "dignified", "unparalleled", "peerless",
"unique", "matchless", "fear-defying", "undaunted", "high-flying", "pioneering"
];

return list[Math.floor(Math.random() * list.length)] + "-tournament";
}