import $store from '../store/store.js';
import { createMessage } from '../views/chat/methods.js';
import { $id } from './dollars.js';
import $callToast from './callToast.js';

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.currentRoute = undefined;
        this.currentConversation = undefined;

        // this.routeMethods = {
        //     "chat": function() {
                
                
        //         // const container = $id("chat-view-messages-container");
        //         // const newMessage = createMessage(message);
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
            this.receiveMessage(data);
            // this.routeMethods[message.messageType].bind(this)();
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

        // this.socket.addEventListner("message", this.receiveMessage);
    }
    
    // Allowd types are:
    // - chat (for sending chat messages)
    // - seen (for marking conversation as seen) "id": <conversationid>
    sendMessage(message) {
        this.socket.send(JSON.stringify(message));
        console.log("FE -> BE:", message);
    }

    // The backend send:
    // - chat (for receiving chat messages)
    // - update 
    //      - "what": "conversation","all"
    //      - "id": <conversationid>
    receiveMessage(message) {

        console.log("BE -> FE:", message);

        switch (message.messageType) {
            case "chat":
                if (this.currentRoute == "chat")
                    this.processIncomingChatMessageChatView(message);
                return ;

            case "updateBadge":
                if (message.what == "all")
                    this.updateNavBarBadge(message.value);
                else if (message.what == "conversation")
                    this.updateConversationBadge(message);
                return ;
        }

        if (!message.toastMessage) {
            console.log(message);
            $callToast("error", "no toast message delivered");
        }
        else
            $callToast("success", message.toastMessage);

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
        // this.socket.removeEventListner("message", this.receiveMessage);
    }

    processIncomingChatMessageChatView(message) {
        if (this.currentConversation == message.conversationId) {
            $id("chat-view-messages-container").prepend(createMessage(message));
            
            // send seen message
            this.sendMessage({messageType: "seen", conversationId: this.currentConversation});
        }

        // TODO: push the card to the top of the conversation list
        $id("chat-view-conversations-container").prepend($id("chat-view-conversation-card-" +  message.conversationId));

    }

    updateConversationBadge(message) {
        const element = $id("chat-view-conversation-card-" +  message.id);
        console.log("element", element);
        const seenCouterContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
        console.log("container", seenCouterContainer);
        seenCouterContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = message.value;
        console.log("container", seenCouterContainer);
        console.log("updating to ", message.value);

        if (message.value == "0")
            seenCouterContainer.style.display = "none";
        else 
            seenCouterContainer.style.display = "flex";
    }

    updateNavBarBadge(value) {
        if (value != 0)
            $id("chat-nav-badge").textContent = value;
        else
            $id("chat-nav-badge").textContent = "";
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

