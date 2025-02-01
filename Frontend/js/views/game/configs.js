import { translate } from '../../locale/locale.js';
import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';
import { changeGameState } from './methods.js';
import WebSocketManagerGame from '../../abstracts/WebSocketManagerGame.js';

export default {
    attributes: {
        gameId: null,
        loading: false,
    },

    methods: {
        listenerLeaveLobby() {
            // TODO: Close WS connection
            // redir home
            router('/');
        },

        listenerQuitGame() {
            // TODO:Check if allowed to quit
                // Quit game
                call(`game/delete/${this.gameId}/`, 'DELETE')
                // Close WS connection
                // Redir home
                router('/');
        },

        initListeners(init = true) {
            const buttonLeaveLobby = this.domManip.$id("button-leave-lobby");
            const buttonQuitGame = this.domManip.$id("button-quit-game");
            if (!buttonLeaveLobby || !buttonQuitGame) {
                console.warn("Button not found. Please check the button id.");
                return;
            }

            if (init) {
                buttonLeaveLobby.name = translate("game", "button-leave-lobby");
                buttonLeaveLobby.render();
                buttonQuitGame.name = translate("game", "button-quit-game");
                buttonQuitGame.render();
                this.domManip.$on(buttonLeaveLobby, "click", this.listenerLeaveLobby);
                this.domManip.$on(buttonQuitGame, "click", this.listenerQuitGame);
                return ;
            }

            if (!init) {
                if (buttonLeaveLobby) {
                    // Remove the event listener if exists
                    if (buttonLeaveLobby.eventListeners)
                        this.domManip.$off(buttonLeaveLobby, "click");
                    if (buttonQuitGame.eventListeners)
                        this.domManip.$off(buttonQuitGame, "click");
                }
            }
        },
        initAndTranslate() {
            // Set default values
            // TODO: we should store the default avatar filename somwhere i guess
            // Player 1
            this.domManip.$id("player-1-avatar").src = window.origin + '/media/avatars/' + '54c455d5-761b-46a2-80a2-7a557d9ec618.png'
            this.domManip.$id("player-1-username").innerText = translate("game", "loading...")

            // Player 2
            this.domManip.$id("player-2-avatar").src = window.origin + '/media/avatars/' + '54c455d5-761b-46a2-80a2-7a557d9ec618.png'
            this.domManip.$id("player-2-username").innerText = translate("game", "loading...")

        },

        async loadDetails() {
            // To avoid multiple calls at the same time
            if(this.loading) {
                console.warn("Already loading view. Please wait.");
                return Promise.resolve();
            }
            this.loading = true;

            // Load the data from REST API
            return call(`game/lobby/${this.gameId}/`, 'GET')
                .then(data => {
                    console.log("data:", data);

                    // Set user cards
                    this.domManip.$id("player-1-username").innerText = "@" + data.username
                    this.domManip.$id("player-1-avatar").src = window.origin + '/media/avatars/' + data.userAvatar
                    this.domManip.$id("player-2-username").innerText = "@" + data.opponentUsername
                    this.domManip.$id("player-2-avatar").src = window.origin + '/media/avatars/' + data.opponentAvatar

                    // Set game state
                    changeGameState(data.gameState);

                })
                .catch(error => {
                    router('/');
                    console.error('Error occurred:', error);
                });
        },
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            // Disconnect from Websocket
            // Connect to Websocket
            WebSocketManagerGame.disconnect(this.gameId);

            this.initListeners(false);
        },

        beforeDomInsertion() {

        },

        async afterDomInsertion() {
            this.initAndTranslate();
            this.initListeners();

            // Checking game id
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                console.warn("Invalid game id '%s' from routeParams?.id -> redir to home", this.routeParams.id);
                router('/');
                return;
            }
            this.gameId = this.routeParams.id;
            this.loadDetails()

            // Connect to Websocket
            WebSocketManagerGame.connect(this.gameId);

            // Hide the spinner and show conncted message
            this.domManip.$id("player-1-state-spinner").style.display = "none";
            this.domManip.$id("player-1-state").innerText = translate("game", "ready");
			const gameField = this.domManip.$id("game-field");
			const ctx = gameField.getContext('2d');
			ctx.clearRect(0, 0, gameField.width, gameField.height);

			const borders = {
				rightUpperCorner: {
					x: gameField.width - 5,
					y: 5
				},
				rightLowerCorner: {
					x: gameField.width - 5,
					y: gameField.height - 5
				},
				leftUpperCorner: {
					x: 5,
					y: 5
				},
				leftLowerCorner: {
					x: 5,
					y: gameField.height - 5
				}
			}

			const paddles = {
				leftPaddle: {
					width: 4,
					height: 30,
					x: 10,
					y: gameField.height / 2 - 30 / 2,
				},
				rightPaddle: {
					width: 4,
					height: 30,
					x: gameField.width - 4 - 10,
					y: gameField.height / 2 - 30 / 2
				}
			}

			const ball = {
				x: gameField.width / 2 + 3,
				y: gameField.height / 2 + 3,
				height: 4,
				width: 6,
				speed: 5,
				dx: 5,
				dy: 5
			}

			const drawPaddles = () => {
				ctx.fillStyle = 'white';
				ctx.fillRect(paddles.leftPaddle.x, paddles.leftPaddle.y, paddles.leftPaddle.width, paddles.leftPaddle.height);
				ctx.fillRect(paddles.rightPaddle.x, paddles.rightPaddle.y, paddles.rightPaddle.width, paddles.rightPaddle.height);
			}

			const drawBall = () => {
				ctx.beginPath();
				ctx.moveTo(ball.x, ball.y);
				ctx.lineTo(ball.x - ball.width, ball.y);
				ctx.lineTo(ball.x - ball.width, ball.y - ball.height);
				ctx.lineTo(ball.x, ball.y - ball.height);
				ctx.lineTo(ball.x, ball.y);
				ctx.fill();
				ctx.closePath();
			}

			const drawBorders = () => {
				ctx.strokeStyle = 'white';
				ctx.beginPath();
				ctx.moveTo(5, 5);
				ctx.lineTo(borders.leftLowerCorner.x, borders.leftLowerCorner.y);
				ctx.lineTo(borders.rightLowerCorner.x, borders.rightLowerCorner.y);
				ctx.lineTo(borders.rightUpperCorner.x, borders.rightUpperCorner.y);
				ctx.lineTo(borders.leftUpperCorner.x, borders.leftUpperCorner.y);
				ctx.stroke();
				ctx.closePath();
			}

			const drawFieldSeparator = () => {
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

			const drawField = () => {
				ctx.fillStyle = 'black';
				ctx.fillRect(0, 0, gameField.width, gameField.height);
				

				drawFieldSeparator();
				drawBorders();
				drawPaddles();
				drawBall();
			}

			drawField();

			const goToGameButton = this.domManip.$id("go-to-game");
			goToGameButton.addEventListener('click', () => {
				const gameViewImageContainer = this.domManip.$id("game-view-image-container");
				const gameImageContainer = this.domManip.$id("game-view-map-image");
				const gameImage = gameImageContainer.children[0];
				gameField.style.display = "block";
				gameImage.src = window.location.origin + '/assets/game/maps/ufo.png';
				gameViewImageContainer.style.backgroundImage = "none";
				gameViewImageContainer.style.width= "100%";
				gameImage.style.display = "block";
			});




			// xico's test

			// const canvas = document.getElementById('game-field');
			// const context = canvas.getContext('2d');
			
			// /*=================| Variables |=========================*/
			
			// const paddlePlayer1 = {
			// 	x: 5,
			// 	y: 30,
			// 	height: 35,
			// 	width: 5,
			// 	speed: 2,
			// 	direction: 0,
			// 	color: '#101098'
			// }
			
			// const paddlePlayer2 = {
			// 	x: 290,
			// 	y: 30,
			// 	height: 35,
			// 	width: 5,
			// 	speed: 2, // Easy: 1.5  Medium: 1.7     Hard: 2
			// 	direction: 0,
			// 	color: '#880000'
			// }
			
			// const ball = {
			// 	x: canvas.width / 2,
			// 	y: canvas.height / 2,
			// 	size: 3,
			// 	speed: 3,
			// 	vx: 1,
			// 	vy: 1,
			// 	vectSum: Math.sqrt(Math.pow(1, 2) + Math.pow(1, 2))
			// }
			
			// const game = {
			// 	pointsPlayer1: 0,
			// 	pointsPlayer2: 0,
			// 	initialSpeed: ball.speed,
			// 	speedIncrement: 0.2,
			// 	speedLimit: 6,
			// 	paddleHits: 0,
			// 	serveDirection: -1,
			// }
			
			
			
			// /*=================| Drawing functions |=========================*/
			
			// function drawField(Racket){
			// 	let high = 5;
			// 	context.beginPath();
			// 	while (high < canvas.height){
			
			// 		context.rect((canvas.width / 2) - 1, high, 2, 15);
			// 		context.fillStyle = '#ffffff';
			// 		context.fill();
			// 		high += 21;
			// 	}
			// 	context.closePath();
			
			// 	// Draw the Player 1 limit
			// 	context.beginPath();
			// 	context.rect(0, 0, 10, canvas.height);
			// 	context.fillStyle = '#000032';
			// 	context.fill();
			// 	context.closePath();
			
			// 	// Draw the Player 2 limit
			// 	context.beginPath();
			// 	context.rect(canvas.width - 10, 0, 10, canvas.height);
			// 	context.fillStyle = '#320000';
			// 	context.fill();
			// 	context.closePath();
			
			// }
			
			// function drawRacket(racket){
			// 	context.beginPath();
			// 	context.rect(racket.x, racket.y, racket.width, racket.height);
			// 	context.fillStyle = racket.color;
			// 	context.fill();
			// 	context.closePath();
			// }
			
			// function drawBall(){
			// 	context.beginPath();
			// 	context.arc(ball.x, ball.y, ball.size, 0, 2 * Math.PI, true);
			// 	context.fillStyle = '#ffffff';
			// 	context.fill();
			// 	context.closePath();
			// }
			
			// function drawAll(){
			// 	context.clearRect(0, 0, canvas.width, canvas.height);
			// 	drawField();
			// 	drawBall();
			// 	drawRacket(paddlePlayer2);
			// 	drawRacket(paddlePlayer1);
			// }
			
			// /*=================| Movement functions |=========================*/
			
			// function moveRaquet1(){
			// 	const temp = paddlePlayer1.y + (paddlePlayer1.direction * paddlePlayer1.speed);
			// 	if (temp >= 0 && temp <= canvas.height - paddlePlayer1.height)
			// 		paddlePlayer1.y = temp;
			// }
			
			// function moveRaquet2(){
			
			// 	const midPaddle = paddlePlayer2.y + (paddlePlayer2.height / 2);
			// 	const differential = midPaddle - ball.y;
			// 	let temp = 0;
			
			// 	if (differential >= paddlePlayer2.speed)
			// 		temp = paddlePlayer2.y - paddlePlayer2.speed;
			// 	else if (differential <= paddlePlayer2.speed)
			// 		temp = paddlePlayer2.y + paddlePlayer2.speed;
			// 	else
			// 		temp = ball.y - (paddlePlayer2.height / 2);
			
			// 	if (temp >= 0 && temp <= canvas.height - paddlePlayer2.height)
			// 		paddlePlayer2.y = temp;
			// }
			
			// function changeBallDirection(){
			// 	if (ball.x >= canvas.width / 2)
			// 		racket = paddlePlayer2;
			// 	else
			// 		racket = paddlePlayer1;
			
			// 	ballPos = ball.y - (racket.y  + (racket.height / 2));
			
			// 	ball.vy = ballPos / (racket.height / 2);
			
			// 	if (ball.vx < 0)
			// 		sign = -1;
			// 	else
			// 		sign = 1;
			
			// 	ball.vx = Math.sqrt(Math.pow(ball.vectSum, 2) - Math.pow(ball.vy, 2)) * sign;
			// }
			
			// function resetGame(){
			
			// 	// Atribute the point
			// 	if (ball.x > (canvas.width / 2))
			// 		game.pointsPlayer1++;
			// 	else
			// 		game.pointsPlayer2++;
			
			// 	console.log('P1', game.pointsPlayer1, ':', game.pointsPlayer2, 'P2');
			
			// 	// Reset speed
			// 	ball.speed = game.initialSpeed;
				
			// 	// Reset direction
			// 	if ((game.pointsPlayer1 + game.pointsPlayer2) % 2 == 0)
			// 		ball.vx *= -1;
			// 	ball.vy = 0;
			
			// 	// Reset position
			// 	ball.x = canvas.width / 2;
			// 	ball.y = canvas.height / 2;
			// }
			
			// function changeBallSpeed(){
			// 	if (game.paddleHits % 2 == 1)
			// 		return ;
			// 	ball.speed += game.speedIncrement;
			// 	if (ball.speed > game.speedLimit)
			// 		ball.speed = game.speedLimit;
			// }
			
			// function moveBall(){
			// 	ball.x = ball.x + (ball.vx * ball.speed);
			// 	ball.y = ball.y + (ball.vy * ball.speed);
			
			// 	// if the ball passes the paddles
			// 	if (ball.x - 1.5 <= 0 || ball.x + 1.5 >= canvas.width)
			// 	{
			// 		// ball.vx *= -1;
					
			// 		resetGame();
			// 	}
				
			// 	// if the ball hits the horizontal walls
			// 	if (ball.y - 1.5 <= 0 && ball.vy < 0 || ball.y + 1.5 >= canvas.height && ball.vy > 0)
			// 		ball.vy *= -1;
			
			// 	// if the ball hits the raquets
			// 	if ((ball.x - 1.5 <= 10 && ball.y >= paddlePlayer1.y && ball.y <= paddlePlayer1.y + paddlePlayer1.height)
			// 			|| ball.x + 1.5 >= canvas.width - 10 && ball.y >= paddlePlayer2.y && ball.y <= paddlePlayer2.y + paddlePlayer2.height)
			// 	{
			// 		ball.vx *= -1;
			// 		game.paddleHits++;
			// 		changeBallDirection();
			// 		changeBallSpeed();
			// 	}
			
			// }
			
			// /*=================| Image update and callback |=========================*/
			
			// function updateImage(){
			// 	moveRaquet1();
			// 	moveRaquet2();
			// 	moveBall();
			// 	drawAll();
			// 	requestAnimationFrame(updateImage);
			// }
			
			
			// updateImage();
			
			// function keyPress(e){
			// 	console.log('here');
			// 	if (e.key === 'w' || e.key === 'W')
			// 		paddlePlayer1.direction = -1;
			// 	if (e.key === 's' || e.key === 'S')
			// 		paddlePlayer1.direction = 1;
			// }
			
			// function keyRelease(e){
			// 	if (e.key === 'w' || e.key === 'W' || e.key === 's' || e.key === 'S')
			// 		paddlePlayer1.direction = 0;
			// }
			
			// document.addEventListener('keydown', keyPress);
			// document.addEventListener('keyup', keyRelease);

			// drawAll();
        },
    }
}