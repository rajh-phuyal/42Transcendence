import $store from '../store/store.js';
import { createMessage } from '../views/chat/methods.js';
import { $id, $on } from './dollars.js';
import $callToast from './callToast.js';
import router from '../navigation/router.js';

const { hostname } = window.location;

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.currentRoute = undefined;
        this.currentConversation = undefined;
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
                else
                    $callToast("error", "Need to implement the notification for chat as toast! issue #217");
                return ;

            case "updateBadge":
                if (message.what == "all")
                    this.updateNavBarBadge(message.value);
                else if (message.what == "conversation")
                    this.updateConversationBadge(message);
                return ;

            case "newConversation":
                this.createConversationCard(message);
                return ;

            case "error":
                $callToast("error", message.message);
                return ;
        }

        console.warn("FE doen't know what to do with this type:", message);
    }
    
    // Disconnect from WebSocket TODO: #207 we need to be able to specify which connection to close
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
            
            // send seen message if it is not ur own message
            if (message.userId != $store.fromState("user").id)
                this.sendMessage({messageType: "seen", conversationId: this.currentConversation});
        }
        $id("chat-view-conversations-container").prepend($id("chat-view-conversation-card-" +  message.conversationId));
    }

    updateConversationBadge(message) {
        const element = $id("chat-view-conversation-card-" +  message.id);
        const seenCouterContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
        seenCouterContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = message.value;
        if (message.value == "0")
            seenCouterContainer.style.display = "none";
        else 
            seenCouterContainer.style.display = "flex";
    }

    updateNavBarBadge(value) {
        $id("chat-nav-badge").textContent = value || "";
    }

    createConversationCard(message) {
        let conversation = $id("chat-view-conversation-card-template").content.cloneNode(true);
        let container = conversation.querySelector(".chat-view-conversation-card");
        container.id = "chat-view-conversation-card-" +  message.conversationId; 
        container.setAttribute("conversation_id", message.conversationId);
        container.setAttribute("last-message-time", message.lastUpdate);
        
        // Avatar
        conversation.querySelector(".chat-view-conversation-card-avatar").src = window.origin + '/media/avatars/' + message.conversationAvatar;

        // User
        conversation.querySelector(".chat-view-conversation-card-username").textContent = message.conversationName;

        // Seen container
        let unseenContainer = conversation.querySelector(".chat-view-conversation-card-unseen-container");
        if (message.unreadCounter == 0)
            unseenContainer.style.display = "none";
        else {
            unseenContainer.style = "flex";
            unseenContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = message.unreadCounter;
        }
        let conversationsContainer = $id('chat-view-conversations-container');
        conversationsContainer.prepend(conversation);
        // TODO: issue #121 This doens't work sinc the router is not getting the chat it same bug than for profile
        $on(container, "click", () => router("chat", {id: message.conversationId}))
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

