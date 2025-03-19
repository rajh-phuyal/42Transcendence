import $store from '../store/store.js';
import { $id } from './dollars.js';
import $callToast from './callToast.js';
import { updateView } from '../views/tournament/methodsView.js';
import { updateMembers } from '../views/tournament/methodsMembers.js';
import { updateRankTable, updateFinalsDiagram, updatePodium } from '../views/tournament/methodsRank.js';
import { updateGameCard } from '../views/tournament/methodsGames.js';
import { createGameList } from '../views/tournament/methodsGames.js';


import { processIncomingWsChatMessage, updateConversationBadge, createConversationCard, updateTypingState } from '../views/chat/methods.js';
import { processIncomingReloadMsg } from '../views/profile/methods.js';
import { audioPlayer } from '../abstracts/audio.js';
import { tournamentData } from '../views/tournament/objects.js';
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
    // - typing (for sending typing indicator)
    sendMessage(message) {
        this.socket.send(JSON.stringify(message));
        console.log("FE -> BE:", message);
    }

    // The backend send:
    // - chat (for receiving chat messages)
    // - update
    //      - "what": "conversation","all"
    //      - "id": <conversationid>

    // TODO: make sure all WS messages cases are checking if the view that is loaded is the correct one
    receiveMessage(message) {
        console.log("BE -> FE:", message);
        switch (message.messageType) {
            // BASIC MESSAGES
            case "error":
                $callToast("error", message.message);
                return ;
            case "info":
                $callToast("sucess", message.message);
                return ;

            // CHAT RELATED MESSAGES
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
            case "typing":
                updateTypingState(message)
                return ;

            // TOURNAMENT RELATED MESSAGES
            case "tournamentInfo":
                if (this.currentRoute == "tournament"){
                    updateView(message.state);
                }
                return ;
            case "tournamentMember":
                // TODO: maybe this is not used anymore!
                return ;
            case "tournamentMembers":
                tournamentData.all.tournamentMembers = message.tournamentMembers;
                updateView();
            /*         updateRankTable(message.tournamentMembers);
                console.log("tournanemtMembers:", message.tournamentMembers);
                console.log("Length!!!!", message.tournamentMembers.length);
                if (message.tournamentMembers.length == 3) {
                    console.log("third member:", message.tournamentMembers.find(member => member.rank === 3));
                    updatePodium(message.tournamentMembers.find(member => member.rank === 3), "third", false);
                } */
                return ;
            case "tournamentGame":
                updateGameCard(message.TournamentGame);
                updateFinalsDiagram(message.TournamentGame);
                return ;

            // PROFILE RELATED MESSAGES
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

    setCurrentRoute(route) {
        this.currentRoute = route;
    }

    getCurrentRoute() {
        return this.currentRoute;
    }

    reconnect() {
        this.disconnect();
        this.connect();
    }
}

// Export a single instance to be used across the app
export default new WebSocketManager();

