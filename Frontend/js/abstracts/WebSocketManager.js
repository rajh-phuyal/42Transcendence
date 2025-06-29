import $store from '../store/store.js';
import $callToast from './callToast.js';
import { $id } from './dollars.js';
import { updateView } from '../views/tournament/methodsView.js';
import { updateDataMember, updateDataGame } from '../views/tournament/methodsData.js';
import { updatePodium, updateFinalsDiagram } from '../views/tournament/methodsRankFinals.js';
import { processIncomingWsChatMessage, updateConversationBadge, createConversationCard, updateTypingState } from '../views/chat/methods.js';
import { processIncomingReloadMsg } from '../views/profile/methods.js';
import { audioPlayer } from '../abstracts/audio.js';
import { tournamentData } from '../views/tournament/objects.js';
const { hostname } = window.location;

class WebSocketManager {
    constructor() {
        this.socket = null;
    }

    // Connect to WebSocket with the provided token
    connect() {
        if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) {
            return;
        }
        // Don't try to connect if not authenticated
        if (!$store.fromState('isAuthenticated')) {
            $store.addMutationListener('setIsAuthenticated', (isAuthenticated) => {
                if (!isAuthenticated) return;
                this.connect();
            });
            return;
        }

        const host = hostname;
        const socketUrl = `wss://${host}/ws/app/main/`;
        try {
            this.socket = new WebSocket(socketUrl);

            // Log connection events
            this.socket.onopen = () => {
                console.log("WebSocket connected:", socketUrl);
                $store.commit("setWebSocketIsAlive", true);
            };

            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.receiveMessage(data);
                // this.routeMethods[message.messageType].bind(this)();
                // Dispatch data to appropriate handlers based on message type
            };

            this.socket.onclose = (event) => {
                console.log("WebSocket closed:", event);
                $store.commit("setWebSocketIsAlive", false);
            }

        } catch (error) {
            console.error("WebSocket connection error:", error);
            $store.commit("setWebSocketIsAlive", false);
        };

        this.socket.onerror = (error) => {
            console.error("WebSocket error:", error);
            $store.commit("setWebSocketIsAlive", false);
        };
    }

    // Allowd types are:
    // - chat (for sending chat messages)
    // - seen (for marking conversation as seen) "id": <conversationid>
    // - typing (for sending typing indicator)
    sendMessage(message) {
        this.socket.send(JSON.stringify(message));
    }

    receiveMessage(message) {
        // console.log("BE -> FE:", message);
        const currentRoute = $store.fromState("currentRoute");

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
                if (currentRoute == "chat") {
                    audioPlayer.playSound("chat");
                    processIncomingWsChatMessage(message);
                } else {
                    // console.log("message:", message);
                    $callToast("message", message.content, {id: message.conversationId, username: message.username, avatar: message.avatar});
                }
                return ;
            case "updateBadge":
                if (message.what == "all")
                    this.updateNavBarBadge(message.value);
                else if (message.what == "conversation" && currentRoute == "chat")
                    updateConversationBadge(message.id, message.value);
                return ;
            case "newConversation":
                createConversationCard(message, false);
                return ;
            case "typing":
                updateTypingState(message)
                return ;

            // TOURNAMENT RELATED MESSAGES
            case "clientRole":
                if (currentRoute == "tournament"){
                    if (message.tournamentId !== tournamentData.tournamentInfo.id) {
                        console.log("Received clientRole for different tournament. Ignoring it");
                        return ;
                    }
                    tournamentData.clientRole = message.clientRole;
                    updateView();
                }
                return ;
            case "tournamentInfo":
                if (currentRoute == "tournament"){
                    if (message.tournamentInfo.id !== tournamentData.tournamentInfo.id) {
                        console.log("Received tournamentInfo for different tournament. Ignoring it");
                        return ;
                    }
                    tournamentData.tournamentInfo = message.tournamentInfo;
                    updateView();
                }
                return ;
            case "tournamentMember":
                if (currentRoute == "tournament"){
                    if (message.tournamentId !== tournamentData.tournamentInfo.id) {
                        console.log("Received tournamentMember for different tournament. Ignoring it");
                        return ;
                    }
                    updateDataMember(message.tournamentMember);
                    updateView();
                }
                return ;
            case "tournamentMembers":
                if (currentRoute == "tournament"){
                    if (message.tournamentId !== tournamentData.tournamentInfo.id) {
                        console.log("Received tournamentMember for different tournament. Ignoring it");
                        return ;
                    }
                    tournamentData.tournamentMembers = message.tournamentMembers;
                    if (message.tournamentMembers.length == 3) {
                        console.log("third member:", message.tournamentMembers.find(member => member.rank === 3));
                        updatePodium(message.tournamentMembers.find(member => member.rank === 3), "third", false);
                    }
                    updateView();
                }
                return ;
            case "tournamentGame":
                if (currentRoute == "tournament"){
                    if (message?.tournamentId !== tournamentData?.tournamentInfo?.id) {
                        console.log("Received tournamentMember for different tournament. Ignoring it");
                        return ;
                    }
                    updateDataGame(message.tournamentGame);
                    updateFinalsDiagram(message.tournamentGame);
                    updateView(true);
                }
                return ;

            // PROFILE RELATED MESSAGES
            case "reloadProfile":
                if (currentRoute === "profile")
                    processIncomingReloadMsg(message);
                return ;
        }

        console.log("FE doen't know what to do with this type:", message);
        $callToast("sucess", message.message);
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        // this.socket.removeEventListner("message", this.receiveMessage);
    }

    updateNavBarBadge(value) {
		if (value > 99)
			value = "99+";
        $id("nav-chat-badge").innerHTML = value || "";
    }
}

// Export a single instance to be used across the app
export default new WebSocketManager();

