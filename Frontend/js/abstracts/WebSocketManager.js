import $store from '../store/store.js';
const { hostname } = window.location;

class WebSocketManager {
    constructor() {
        this.socket = null;
    }

    // Connect to WebSocket with the provided token
    connect(token) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket already connected.");
            return;
        }

        // const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        // TODO: i am not sure if this is the right way to do issue #190
        const protocol = 'ws://';
        const resolvedHostname = hostname === 'localhost' ? '127.0.0.1' : hostname;
        const socketUrl = `${protocol}${resolvedHostname}:8000/ws/app/main/?token=${token}`;
        console.log("Connecting to WebSocket:", socketUrl);

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
}

// Export a single instance to be used across the app
export default new WebSocketManager();
