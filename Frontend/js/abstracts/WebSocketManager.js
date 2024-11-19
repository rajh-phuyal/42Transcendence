import $store from '../store/store.js';

class WebSocketManager {
    constructor() {
        this.socket = null;
    }

    // Connect to WebSocket with the provided token
    connect() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket already connected.");
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const socketUrl = `${protocol}127.0.0.1:8000/ws/app/main/`;

        this.socket = new WebSocket(socketUrl);

        // Log connection events
        this.socket.onopen = () => {
            console.log("WebSocket connected.");
            $store.commit("setWebSocketIsAlive", true);
        };

		this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Message received from server:", data);
            // Dispatch data to appropriate handlers based on message type
        };

        this.socket.onclose = () => {
            console.log("WebSocket disconnected.");
            $store.commit("setWebSocketIsAlive", false);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            $store.commit("setWebSocketIsAlive", false);
        };
    }

    // Disconnect from WebSocket TODO: we need to be able to specify which connection to close
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            console.log("WebSocket connection closed.");
        } else {
            console.log("WebSocket is not connected.");
        }
    }

    refreshToken() {
        this.disconnect();
        this.connect();
    }
}

// Export a single instance to be used across the app
export default new WebSocketManager();
