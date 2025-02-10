import { gameObject } from './objects.js';
import { $id } from '../../abstracts/dollars.js';
import { percentageToPixels, showPowerupStatus } from './methods.js';
import { audioPlayer } from '../../abstracts/audio.js';
import { updateReadyStateNodes } from './methods.js';

// ############## VARIABLES ##############
const borders = {
	rightUpperCorner: {
		x: 0,
		y: 0
	},
	rightLowerCorner: {
		x: 0,
		y: 0
	},
	leftUpperCorner: {
		x: 0,
		y: 0
	},
	leftLowerCorner: {
		x: 0,
		y: 0
	}
};

const segmentDisplayDigits = [
	{
		top: true,
		topRight: true,
		middle: false,
		topLeft: true,
		bottomRight: true,
		bottom: true,
		bottomLeft: true,
	},
	{
		top: false,
		topRight: true,
		middle: false,
		topLeft: false,
		bottomRight: true,
		bottom: false,
		bottomLeft: false,
	},
	{
		top: true,
		topRight: true,
		middle: true,
		topLeft: false,
		bottomRight: false,
		bottom: true,
		bottomLeft: true,
	},
	{
		top: true,
		topRight: true,
		middle: true,
		topLeft: false,
		bottomRight: true,
		bottom: true,
		bottomLeft: false,
	},
	{
		top: false,
		topRight: true,
		middle: true,
		topLeft: true,
		bottomRight: true,
		bottom: false,
		bottomLeft: false,
	},
	{
		top: true,
		topRight: false,
		middle: true,
		topLeft: true,
		bottomRight: true,
		bottom: true,
		bottomLeft: false,
	},
	{
		top: true,
		topRight: false,
		middle: true,
		topLeft: true,
		bottomRight: true,
		bottom: true,
		bottomLeft: true,
	},
	{
		top: true,
		topRight: true,
		middle: false,
		topLeft: false,
		bottomRight: true,
		bottom: false,
		bottomLeft: false,
	},
	{
		top: true,
		topRight: true,
		middle: true,
		topLeft: true,
		bottomRight: true,
		bottom: true,
		bottomLeft: true,
	},
	{
		top: true,
		topRight: true,
		middle: true,
		topLeft: true,
		bottomRight: true,
		bottom: false,
		bottomLeft: false,
	}
]

const segmentDisplaySettings = {
	top: {
		width: 6,
		height: 2,
		x: 0,
		y: 0,
	},
	topRight: {
		width: 2,
		height: 7,
		x: 0,
		y: 0,
	},
	middle: {
		width: 6,
		height: 2,
		x: 0,
		y: 0,
	},
	topLeft: {
		width: 2,
		height: 7,
		x: 0,
		y: 0,
	},
	bottomRight: {
		width: 2,
		height: 7,
		x: 0,
		y: 0,
	},
	bottom: {
		width: 6,
		height: 2,
		x: 0,
		y: 0,
	},
	bottomLeft: {
		width: 2,
		height: 7,
		x: 0,
		y: 0,
	}
}

const getSegments = (playerScore) => {
	let score;
	let segment;
	const segmentsList = [];

	if (playerScore === 0)
		return [segmentDisplayDigits[0]];

	while (playerScore) {
		score = playerScore % 10;
		playerScore = Math.floor(playerScore / 10);
		segment = segmentDisplayDigits.find((element, index) => {
			if (index === score)
				return element;
		});
		segmentsList.push(segment);
	}
	return segmentsList;
}

const drawScore = (ctx, gameField, playerScore, boardSide) => {
	const segments = getSegments(playerScore);
	const digitSeparator = boardSide === "right" ? -15 : 15;
	const digit = { ...segmentDisplaySettings };

	digit.top.x = gameField.width / 2 - digit.top.width/2 + (digitSeparator < 0 ? -20 : 20);
	digit.top.y = digit.top.height + 2;
	digit.topRight.x = digit.top.x + digit.top.width + 1;
	digit.topRight.y = digit.top.y;
	digit.middle.x = digit.top.x;
	digit.middle.y = digit.topRight.y + digit.topRight.height;
	digit.topLeft.x = digit.top.x - digit.topLeft.width - 1;
	digit.topLeft.y = digit.top.y;

	digit.bottomRight.x = digit.topRight.x;
	digit.bottomRight.y = digit.middle.y + digit.middle.height - 1;
	digit.bottom.x = digit.top.x;
	digit.bottom.y = digit.bottomRight.y + digit.bottomRight.height - 2;
	digit.bottomLeft.x = digit.topLeft.x;
	digit.bottomLeft.y = digit.bottomRight.y;

	if (boardSide === "left")
		segments.reverse();

	segments.forEach((segment, index) => {
		const segmentKeys = Object.keys(segment);
		segmentKeys.forEach((key) => {
			if (segment[key]) {
				ctx.fillStyle = 'rgb(197, 197, 197)';
				ctx.fillRect(digit[key].x + digitSeparator * index, digit[key].y, digit[key].width, digit[key].height);
			}
			else {
				ctx.fillStyle = 'rgb(33, 33, 33)';
				ctx.fillRect(digit[key].x + digitSeparator * index, digit[key].y, digit[key].width, digit[key].height);
			}
		});
	});
}

// ############## FUNCTIONS ##############
const drawPaddle = (gameField, ctx, side) => {
    const gameFieldHeight = gameField.height;
    const gameFieldWidth = gameField.width;
    let posX, posY, width, height, paddleSpacing;
    width = percentageToPixels('x', gameObject.paddleWidth);
    paddleSpacing = percentageToPixels('x', gameObject.paddleSpacing);
    if (side === "left") {
        height = gameObject.playerLeft.size;
        posX = gameObject.borderStrokeWidth + paddleSpacing;
        posY = gameObject.playerLeft.pos
    }
    else if (side === "right") {
        height = gameObject.playerRight.size;
        posX = gameField.width - gameObject.borderStrokeWidth - paddleSpacing - width;
        posY = gameObject.playerRight.pos
    } else {
        console.error("Invalid side to draw paddle");
        return;
    }
    ctx.fillStyle = 'white';
	ctx.fillRect(posX, posY, width, height);
}

const drawBall = (ctx) => {
	const ballStartPosX = gameObject.ball.posX - (gameObject.ball.width / 2);
	const ballStartPosY = gameObject.ball.posY - (gameObject.ball.height / 2);
	ctx.beginPath();
	ctx.fillRect(ballStartPosX, ballStartPosY, gameObject.ball.width, gameObject.ball.height);
	ctx.fill();
	ctx.closePath();
}

const drawField = (gameField, ctx) => {
    // Black Background
    ctx.setLineDash([]);
	ctx.fillStyle = 'rgba(131, 127, 127, 0.2)';
	ctx.fillRect(0, 0, gameField.width, gameField.height);
    // Middle line
    ctx.strokeStyle = 'white';
    ctx.lineWidth = gameObject.borderStrokeWidth;
    ctx.setLineDash([7, 10]);
    const middleX = (gameField.width /2);
    const middleY = (gameField.height /2);
	ctx.beginPath();
    ctx.moveTo(middleX, middleY);
    ctx.lineTo(middleX, 0);
    ctx.moveTo(middleX, middleY);
    ctx.lineTo(middleX, gameField.height);
    ctx.stroke();
    // Outlines
    ctx.setLineDash([]);
    ctx.strokeRect(0, 0, gameField.width, gameField.height);
    // Draw the rest
	drawPaddle(gameField, ctx, "left");
    drawPaddle(gameField, ctx, "right");
	drawBall(ctx);
	drawScore(ctx, gameField, gameObject.playerLeft.points, "right");
	drawScore(ctx, gameField, gameObject.playerRight.points, "left");
}

export function gameRender () {
	const gameField = $id("game-field");
    const ctx = gameField.getContext('2d');
	ctx.clearRect(0, 0, gameField.width, gameField.height);
	drawField(gameField, ctx);
    // This will only play wall, paddle, score, powerup sounds since the are triggered/send by the be
    // All other sounds are state realated and therfore should be playe by fe function: changeGameState()
    audioPlayer.playSound(gameObject.sound);
    showPowerupStatus(true);
}

export function toggleGamefieldVisible(visible) {
    // TODO:
    if(visible) {
        // Show the game field
        const gameField = $id("game-field");
        const ctx = gameField.getContext('2d');
        ctx.clearRect(0, 0, gameField.width, gameField.height);
        gameRender(gameField, ctx);
        // Play the game music
    } else {
        console.log("TODO");
        // Hide the game field
        // Play the lobby music
    }
}