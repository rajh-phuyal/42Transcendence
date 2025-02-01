import { gameObject } from './objects.js';

// ############## VARIABLES ##############

const borders = {
	rightUpperCorner: {
		x: 0,
		y: 5
	},
	rightLowerCorner: {
		x: 0,
		y: 0
	},
	leftUpperCorner: {
		x: 5,
		y: 5
	},
	leftLowerCorner: {
		x: 5,
		y: 0
	}
};

// const scale = window.devicePixelRatio || 1;
// gameField.width = gameField.width * scale;
// gameField.height = gameField.height * scale;


// ctx.scale(scale, scale);


// ############## FUNCTIONS ##############

const drawPaddles = (gameField, ctx) => {
	ctx.fillStyle = 'white';
	ctx.fillRect(10, gameObject.playerLeft.pos, 4, gameObject.playerLeft.size);
	ctx.fillRect(gameField.width - 4 - 10, gameObject.playerRight.pos, 4, gameObject.playerRight.size);
}

const drawBall = (ctx) => {
	ctx.beginPath();
	ctx.moveTo(gameObject.ball.posX, gameObject.ball.posY);
	ctx.lineTo(gameObject.ball.posX - 6, gameObject.ball.posY);
	ctx.lineTo(gameObject.ball.posX - 6, gameObject.ball.posY - 4);
	ctx.lineTo(gameObject.ball.posX, gameObject.ball.posY - 4);
	ctx.lineTo(gameObject.ball.posX, gameObject.ball.posY);
	ctx.fill();
	ctx.closePath();
}

const drawBorders = (gameField, ctx) => {
	ctx.strokeStyle = 'white';
	ctx.beginPath();
	ctx.moveTo(5, 5);
	borders.rightUpperCorner.x = gameField.width - 5;
	borders.rightLowerCorner.x = gameField.width - 5;
	borders.rightLowerCorner.y = gameField.height - 5;
	borders.leftLowerCorner.y = gameField.height - 5;
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
	let high = 5;
	while (high < gameField.height){

		ctx.rect((gameField.width / 2) - 1, high, 2, 15);
		ctx.fillStyle = '#ffffff';
		ctx.fill();
		high += 21;
	}
	ctx.closePath();
}

const drawField = (gameField, ctx) => {
	ctx.fillStyle = 'black';
	ctx.fillRect(0, 0, gameField.width, gameField.height);
	drawFieldSeparator(gameField, ctx);
	drawBorders(gameField, ctx);
	drawPaddles(gameField, ctx);
	drawBall(ctx);
}

export function gameRender (gameField, ctx) {
	// TODO: DUMMY DATA REMOVE
	gameObject.playerLeft.pos = gameField.height / 2 - 30 / 2;
	gameObject.playerRight.pos = gameField.height / 2 - 30 / 2;
	gameObject.playerLeft.size = 30;
	gameObject.playerRight.size = 30;
	gameObject.ball.posX = gameField.width / 2 + 3;
	gameObject.ball.posY = gameField.height / 2 + 3;
	// TODO: DUMMY DATA REMOVE
	ctx.clearRect(0, 0, gameField.width, gameField.height);
	drawField(gameField, ctx);
}