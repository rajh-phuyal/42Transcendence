import { gameObject } from './objects.js';

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

// const scale = window.devicePixelRatio || 1;
// gameField.width = gameField.width * scale;
// gameField.height = gameField.height * scale;


// ctx.scale(scale, scale);


// ############## FUNCTIONS ##############

const percentageToPixels = (percentage, edgeSize) => {
	return (edgeSize / 100) * percentage;
}

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
	ctx.fillStyle = 'black';
	ctx.fillRect(0, 0, gameField.width, gameField.height);
	drawFieldSeparator(gameField, ctx);
	drawBorders(gameField, ctx);
	drawPaddles(gameField, ctx, normalizedGameObject);
	drawBall(ctx, normalizedGameObject);
}

const normalizeGameObject = (gameObject, gameField) => {
	const normalizedGameObject = { ...gameObject };
	normalizedGameObject.playerLeft.pos = percentageToPixels(gameObject.playerLeft.pos, gameField.height);
	normalizedGameObject.playerRight.pos = percentageToPixels(gameObject.playerRight.pos, gameField.height);
	normalizedGameObject.playerLeft.size = percentageToPixels(gameObject.playerLeft.size, gameField.height);
	normalizedGameObject.playerRight.size = percentageToPixels(gameObject.playerRight.size, gameField.height);
	normalizedGameObject.ball.posX = percentageToPixels(gameObject.ball.posX, gameField.width);
	normalizedGameObject.ball.posY = percentageToPixels(gameObject.ball.posY, gameField.height);
	normalizedGameObject.ball.size = 4;
	return normalizedGameObject;
}

export function gameRender (gameField, ctx) {
	// TODO: DUMMY DATA REMOVE
	const normalizedGameObject = normalizeGameObject(gameObject, gameField);
	// TODO: DUMMY DATA REMOVE
	ctx.clearRect(0, 0, gameField.width, gameField.height);
	drawField(gameField, ctx, normalizedGameObject);
}