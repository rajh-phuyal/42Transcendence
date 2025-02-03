import { gameObject } from './objects.js';
import { $id } from '../../abstracts/dollars.js';

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
	const digitSeparator = boardSide === "left" ? -15 : 15;
	const digit = { ...segmentDisplaySettings };

	digit.top.x = gameField.width / 2 - digit.top.width + (digitSeparator < 0 ? -20 : 20);
	digit.top.y = digit.top.height;
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

	if (boardSide === "right")
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

// const scale = window.devicePixelRatio || 1;
// gameField.width = gameField.width * scale;
// gameField.height = gameField.height * scale;


// ctx.scale(scale, scale);


// ############## FUNCTIONS ##############


const drawPaddles = (gameField, ctx, normalizedGameObject) => {
	ctx.fillStyle = 'white';
	ctx.fillRect(10, normalizedGameObject.playerLeft.pos - (normalizedGameObject.playerLeft.size / 2), 4, normalizedGameObject.playerLeft.size);
	ctx.fillRect(gameField.width - 4 - 10, normalizedGameObject.playerRight.pos - (normalizedGameObject.playerRight.size / 2), 4, normalizedGameObject.playerRight.size);
}

const drawBall = (ctx, normalizedGameObject) => {
	const ballStartPosX = normalizedGameObject.ball.posX - (normalizedGameObject.ball.size / 2);
	const ballStartPosY = normalizedGameObject.ball.posY - (normalizedGameObject.ball.size / 2);
	ctx.beginPath();
	ctx.fillRect(ballStartPosX, ballStartPosY, normalizedGameObject.ball.size, normalizedGameObject.ball.size);
	ctx.fill();
	ctx.closePath();
}

const drawBorders = (gameField, ctx) => {
	ctx.strokeStyle = 'white';
	ctx.beginPath();
	ctx.moveTo(0, 0);
	borders.rightUpperCorner.x = gameField.width;
	borders.rightLowerCorner.x = gameField.width;
	borders.rightLowerCorner.y = gameField.height;
	borders.leftLowerCorner.y = gameField.height;
	ctx.lineTo(borders.leftLowerCorner.x, borders.leftLowerCorner.y);
	ctx.lineTo(borders.rightLowerCorner.x, borders.rightLowerCorner.y);
	ctx.lineTo(borders.rightUpperCorner.x, borders.rightUpperCorner.y);
	ctx.lineTo(borders.leftUpperCorner.x, borders.leftUpperCorner.y);
	ctx.stroke();
	ctx.closePath();
}

const drawFieldSeparator = (gameField, ctx) => {
	ctx.strokeStyle = 'white';
	ctx.beginPath();
	let high = 0;
	while (high < gameField.height){
		ctx.rect((gameField.width / 2) - 1, high, 2, 15);
		ctx.fillStyle = '#ffffff';
		ctx.fill();
		high += 21;
	}
	ctx.closePath();
}

const drawField = (gameField, ctx, normalizedGameObject) => {
	ctx.fillStyle = 'rgba(0, 0, 0, 0)';
	ctx.fillRect(0, 0, gameField.width, gameField.height);
	drawFieldSeparator(gameField, ctx);
	drawBorders(gameField, ctx);
	drawPaddles(gameField, ctx, normalizedGameObject);
	drawBall(ctx, normalizedGameObject);
	drawScore(ctx, gameField, normalizedGameObject.playerLeft.points, "left");
	drawScore(ctx, gameField, normalizedGameObject.playerRight.points, "right");
}


export function gameRender () {
	const gameField = $id("game-field");
    const ctx = gameField.getContext('2d');
	ctx.clearRect(0, 0, gameField.width, gameField.height);
	drawField(gameField, ctx, gameObject);
}