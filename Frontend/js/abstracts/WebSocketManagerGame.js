import $store from '../store/store.js';
import $callToast from './callToast.js';
import { endGameLoop } from '../views/game/loop.js';
import { updateReadyStatefromWS, updateGameObjects } from '../views/game/methods.js';
import { gameObject } from '../views/game/objects.js';
const { hostname } = window.location;

class WebSocketManagerGame {
    constructor() {
        this.socket = null;
        this.gameId = null;
    }

    // Connect to WebSocket with the provided token
    async connect(gameId = undefined) {
        if (!gameId) {
            console.warn("No gameId provided to connect to GAME WebSocket");
            return ;
        }
        this.gameId = gameId;

        if (this.socket && this.socket.readyState === WebSocket.OPEN)
            return;
        // TODO: check if connected to correct game @xico this shouldn't be a big problem since we always pass the gameId as a parameter
        // This connect function is called when we route to a game. So when we leave the game view to another view, we first disconnect the socket
        // and then connect to the new game. So we technically don't need to check if we are connected to the correct game. I guess...
        // We could check if this.gameId !== undefined. If it is not undefined, first close the old connection and then continue.
        // Not sure if this breaks anything. So up to you @xico. Implement the fix or remove this comment. :D

        // Don't try to connect if not authenticated
        if (!$store.fromState('isAuthenticated')) {
            $store.addMutationListener('setIsAuthenticated', (isAuthenticated) => {
                if (!isAuthenticated) return;
                this.connect();
            });
            return;
        }

        const host = hostname;
        const socketUrl = `wss://${host}/ws/app/game/${gameId}/`;

        try {
            this.socket = new WebSocket(socketUrl);

            // Log connection events
            this.socket.onopen = () => {
                // console.log("GAME WebSocket connected: ", gameId);
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.receiveMessage(data);
            };

        } catch (error) {
            console.error("GAME WebSocket connection error:", error);
        };

        this.socket.onerror = (error) => {
            console.error("GAME WebSocket error:", error);
        };
        gameObject.wsConnection = true;
    }

    sendMessage(message) {
        this.socket.send(JSON.stringify(message));
    }

    receiveMessage(message) {
        // console.log("GAME: BE -> FE:", message);

        switch (message.messageType) {
            case "playersReady":
                updateReadyStatefromWS(message);
                return ;
            case "gameState":
                //console.log("got game state", message);
                updateGameObjects(message);
                return;
        }

        console.warn("WS GAME: FE doen't know what to do with this type:", message);
        $callToast("error", message.message);
    }

    disconnect() {
        gameObject.wsConnection = false;
        endGameLoop();
        this.gameId = null;
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            // console.log("GAME WebSocket connection closed.");
        } else {
            // console.log("GAME WebSocket is not connected.");
        }
    }
}

// Export a single instance to be used across the app
export default new WebSocketManagerGame();

