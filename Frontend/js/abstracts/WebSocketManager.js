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

        // Don't try to connect if not authenticated
        if (!$store.fromState('isAuthenticated')) {
            console.log("Not connecting WebSocket - user not authenticated");
            return;
        }

        const host = window.location.host;
        const protocol = 'wss://';
        const socketUrl = `${protocol}${host}/ws/app/main/`;

        console.log("Connecting to WebSocket:", socketUrl);
        try {
            this.socket = new WebSocket(socketUrl);

            this.socket.onopen = () => {
                console.log("WebSocket connected successfully");
                $store.commit("setWebSocketIsAlive", true);
            };

            this.socket.onerror = (error) => {
                console.error("WebSocket error:", error);
                $store.commit("setWebSocketIsAlive", false);
            };

            this.socket.onclose = (event) => {
                console.log("WebSocket disconnected.", event.reason);
                $store.commit("setWebSocketIsAlive", false);

                // Only attempt reconnect if authenticated
                if ($store.fromState('isAuthenticated')) {
                    setTimeout(() => this.connect(), 2000);
                }
            };

            this.socket.onmessage = (event) => {
                console.log("WebSocket message received:", event.data);
                // Handle incoming messages here
            };
        } catch (error) {
            console.error("WebSocket connection error:", error);
            $store.commit("setWebSocketIsAlive", false);
        }
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
