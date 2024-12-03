import $store from '../store/store.js';
import { createMessage } from '../views/chat/methods.js';
import { $id } from './dollars.js';
import $callToast from './callToast.js';

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.currentRoute = undefined;
        this.currentConversation = undefined;
        this.messageRecieved = undefined;

        // this.routeMethods = {
        //     "chat": function() {
                
                
        //         // const container = $id("chat-view-messages-container");
        //         // const newMessage = createMessage(this.messageRecieved);
        //         // container.insertBefore(newMessage, container.firstChild);
                
        //         // TODO: set the message as seen
                
        //     },
        // }
    }

    


    // Connect to WebSocket with the provided token
    connect(token) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket already connected.");
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
		const socketUrl = `ws://127.0.0.1:8000/ws/app/main/?token=${token}`;
        
        this.socket = new WebSocket(socketUrl);
        
        // Log connection events
        this.socket.onopen = () => {
            console.log("WebSocket connected.");
            $store.commit("setWebSocketIsAlive", true);
        };

		this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("Message received from server:", data);
            console.log("data received:", event.data);
            this.messageRecieved = data;
            this.receiveMessage();
            // this.routeMethods[this.messageRecieved.messageType].bind(this)();
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

        this.socket.addEventListner("message", this.receiveMessage);
    }
    
    // Allowd types are:
    // - chat (for sending chat messages)
    // - seen (for marking conversation as seen) "id": <conversationid>
    sendMessage(message) {
        this.socket.send(JSON.stringify(message));
    }

    // The backend send:
    // - chat (for receiving chat messages)
    // - update 
    //      - "what": "conversation","all"
    //      - "id": <conversationid>
    receiveMessage() {

        console.log("message type:", this.messageRecieved.messageType);

        switch (this.messageRecieved.messageType) {
            case "chat":
                if (this.currentRoute == "chat")
                    this.processIncomingChatMessageChatView();
                return ;

            case "info":
                $callToast("success", this.messageRecieved.message);
                return ;
            
        }

        if (!this.receiveMessage.toastMessage) {
            console.log(this.messageRecieved);
            $callToast("error", "no toast message delivered");
        }
        else
            $callToast("success", this.receiveMessage.toastMessage);

        // TODO: call toast for when the message is recieved in a different route
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
        this.socket.removeEventListner("message", this.receiveMessage);
    }

    processIncomingChatMessageChatView() {
        if (this.currentConversation == this.messageRecieved.conversationId) {
            $id("chat-view-messages-container").prepend(createMessage(this.messageRecieved));
            // TODO: send seen message
        }

        // TODO: push the card to the top of the conversation list

    }

    setCurrentRoute(route) {
        this.currentRoute = route;
    }

    setCurrentConversation(conversationId) {
        this.currentConversation = conversationId;
    }
}

// Export a single instance to be used across the app
export default new WebSocketManager();

