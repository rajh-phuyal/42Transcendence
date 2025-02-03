import $store from '../store/store.js';
import { $id, $on } from './dollars.js';
import $callToast from './callToast.js';
import router from '../navigation/router.js';
import { updateReadyState, updateGameObjects } from '../views/game/methods.js';



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

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("GAME WebSocket already connected.");
            // TODO: check if connected to correct game
            return;
        }

        // Don't try to connect if not authenticated
        if (!$store.fromState('isAuthenticated')) {
            console.log("Not connecting GAME WebSocket - user not authenticated");
            $store.addMutationListener('setIsAuthenticated', (isAuthenticated) => {
                if (!isAuthenticated) return;
                this.connect();
            });
            return;
        }

        const host = hostname;
        const socketUrl = `wss://${host}/ws/app/game/${gameId}/`;

        console.log("Connecting to GAME WebSocket:", socketUrl);
        try {
            this.socket = new WebSocket(socketUrl);

            // Log connection events
            this.socket.onopen = () => {
                console.log("GAME WebSocket connected: ", gameId);
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
    }

    // Allowd types are:
    // - TODO: !!!
    sendMessage(message) {
        console.log("GAME: FE -> BE:", message);
        this.socket.send(JSON.stringify(message));
    }

    // The backend send:
    // - TODO: !!!
    receiveMessage(message) {
        //console.log("GAME: BE -> FE:", message);

        switch (message.messageType) {
            case "playersReady":
                updateReadyState(message);
                return ;
            case "gameState":
                console.log("got game state", message);
                updateGameObjects(message);
                return;

        }

        console.warn("WS GAME: FE doen't know what to do with this type:", message);
        $callToast("error", message.message);
    }

    disconnect() {
        this.gameId = null;
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            console.log("GAME WebSocket connection closed.");
        } else {
            console.log("GAME WebSocket is not connected.");
        }
    }

    // TODO: do we use this?
    reconnect() {
        this.disconnect();
        this.connect();
    }
}

// Export a single instance to be used across the app
export default new WebSocketManagerGame();

