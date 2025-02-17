import $store from '../store/store.js';
import { $id } from './dollars.js';
import $callToast from './callToast.js';
import { updateParticipantsCard, createGameList } from '../views/tournament/methods.js';
import { processIncomingWsChatMessage, updateConversationBadge, createConversationCard } from '../views/chat/methods.js';
import { processIncomingReloadMsg } from '../views/profile/methods.js';
import { audioPlayer } from '../abstracts/audio.js';
const { hostname } = window.location;

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.currentRoute = undefined;
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
            $store.addMutationListener('setIsAuthenticated', (isAuthenticated) => {
                if (!isAuthenticated) return;
                this.connect();
            });
            return;
        }

        const host = hostname;
        const socketUrl = `wss://${host}/ws/app/main/`;

        console.log("Connecting to WebSocket:", socketUrl);
        try {
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

        } catch (error) {
            console.error("WebSocket connection error:", error);
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
                audioPlayer.playSound("chat");
                if (this.currentRoute == "chat")
                    processIncomingWsChatMessage(message);
                else
                    $callToast("error", "Need to implement the notification for chat as toast! issue #217");
                return ;

            case "updateBadge":
                if (message.what == "all")
                    this.updateNavBarBadge(message.value);
                else if (message.what == "conversation" && this.currentRoute == "chat")
                    updateConversationBadge(message.id, message.value);
                return ;

            case "newConversation":
                createConversationCard(message, false);
                return ;

            case "tournamentFan":
                console.warn("TODO!")
                return ;

            case "tournamentState":
                console.warn("TODO!")
                if (this.currentRoute == "tournament"){
                    $id("status").style.backgroundColor = "green";
                }
                return ;

            case "tournamentSubscription":
                console.warn("TODO!")
                if (this.currentRoute == "tournament"){
                    updateParticipantsCard(message);
                    return ;
                }
                break;

            case "gameCreate":
                if (this.currentRoute == "tournament"){
                    createGameList(message.games);
                    return ;
                }
                break ;

            case "gameSetDeadline":
                console.warn("TODO!")
                return ;

            case "gameUpdateScore":
                console.warn("TODO!")
                return ;

            case "gameUpdateState":
                console.warn("TODO!")
                return ;

            case "gameUpdateRank":
                console.warn("TODO!")
                return ;

            case "error":
                $callToast("error", message.message);
                return ;

            case "info":
                $callToast("sucess", message.message);
                return ;

            case "reloadProfile":
                if (this.currentRoute.startsWith("profile"))
                    processIncomingReloadMsg(message, this.currentRoute);
                return ;
        }

        console.warn("FE doen't know what to do with this type:", message);
        $callToast("sucess", message.message);
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

    updateNavBarBadge(value) {
		if (value > 99)
			value = "99+";
        $id("chat-nav-badge").textContent = value || "";
    }

    updateTournamentMemberCard(message) {
        console.log("TODO: Implement updateTournamentMemberCard", message);
    }

    createParticipantCard(userData) {
        // Clone the template
        let card = this.domManip.$id("tournament-list-card-template").content.cloneNode(true);

        // Update the card background color based on user state
        if (userData.userState === "pending") {
            card.querySelector(".card").style.backgroundColor = "grey";
        }

        // Populate the template fields with user data
        //console.log("AAAAAAAAAAAAAA userData:", userData);
        card.querySelector(".user-id .value").textContent = "ID: " + userData.userId;
        card.querySelector(".username .value").textContent = "Username: " + userData.username;
        card.querySelector(".user-avatar").src = "https://localhost/media/avatars/" + userData.userAvatar;
        card.querySelector(".user-avatar").alt = `Avatar of ${userData.username}`;
        card.querySelector(".user-state .value").textContent = "State: " + userData.userState;

        // Return the populated card
        return card;
    }

    setCurrentRoute(route) {
        this.currentRoute = route;
    }

    reconnect() {
        this.disconnect();
        this.connect();
    }
}

// Export a single instance to be used across the app
export default new WebSocketManager();

