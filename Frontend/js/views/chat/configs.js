import call from '../../abstracts/call.js';
import { translate } from '../../locale/locale.js';
import { createMessage } from './methods.js';
import router from '../../navigation/router.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import $store from '../../store/store.js';

export default {
    attributes: {
        chatSocket: null, // WebSocket connection //TODO: not sure if we need this since we are using WebSocketManager
        conversations: [], // All conversations for the user
        selectedConversation: null, // The active conversation
        selectedUser: null, // The user selected in the chat
        messages: [], // Messages of the active conversation

        conversationsContainer: undefined,
        conversations: [],
        conversationParams: undefined,
        lastMessageId: undefined,
        isLoadingMessages: false,
    },

    methods: {
        createLoadingSpinner() {
            const spinnerContainer = document.createElement("div");
            spinnerContainer.style.display = "flex";
            spinnerContainer.style.justifyContent = "center";
            spinnerContainer.style.width = "100%";
            spinnerContainer.style.marginTop = "1rem";
            spinnerContainer.style.marginBottom = "1rem";

            const spinner = document.createElement("div");
            spinner.className = "spinner-grow";
            spinner.innerHTML = `<div class="spinner-grow" role="status"><span class="sr-only"></span></div>`;
            spinnerContainer.appendChild(spinner);
            return spinnerContainer;
        },

        fetchOlderMessages() {
            if (this.isLoadingMessages)
                return ;
            this.isLoadingMessages = true;
            const container = this.domManip.$id("chat-view-messages-container");
            const spinner = this.createLoadingSpinner();

             // Calculate the current scroll position from the bottom
            const previousScrollHeight = container.scrollHeight;
            const previousScrollTop = container.scrollTop;
            container.prepend(spinner);

            // Use the `call` abstraction to fetch older messages
            console.log("Fetching older messages with lastMessageId:", this.lastMessageId);
            const startTime = Date.now();
            call(`chat/load/conversation/${this.conversationParams.conversationId}/messages/?msgid=${this.lastMessageId}`, "PUT")
            .then(data => {

                const elapsedTime = Date.now() - startTime;

                // Ensure spinner stays for at least 0.5 seconds
                const delay = Math.max(500 - elapsedTime, 0);
                // Wait for the delay before processing the response so the spinner is visible :D
                setTimeout(() => {
                    spinner.remove();

                    if (!data.data || data.data.length === 0) {
                        console.log("No more messages to load.");
                        this.isLoadingMessages = false;
                        return;
                    }

                    // Prepend older messages
                    for (const message of data.data) {
                        createMessage(message, true, true);
                    }

                    this.lastMessageId = data.data[data.data.length - 1].id; // Update lastMessageId
                    this.isLoadingMessages = false;
                }, delay);
            })
            .catch(error => {
                console.error("Failed to fetch older messages:", error);
                this.isLoadingMessages = false; // Reset loading state even on error
                spinner.remove(); // Remove spinner on failure
            });
        },

        // Detect scroll-to-top and trigger a function
        initInfiniteScroll() {
            const container = this.domManip.$id("chat-view-messages-container"); // Get the chat container

            this.handleScroll = () => {
                if (container.scrollTop === 0) {
                    this.fetchOlderMessages();
                }
            };

            // Add the event listener
            container.addEventListener("scroll", this.handleScroll);
        },

        removeInfiniteScroll() {
            const container = this.domManip.$id("chat-view-messages-container");
            if (this.handleScroll) {
                container.removeEventListener("scroll", this.handleScroll);
                console.log("Scroll listener removed.");
            }
        },

        initAvatarClick() {
            const avatar = this.domManip.$id("chat-view-header-avatar");
            avatar.style.cursor = "pointer";
            avatar.addEventListener("click", () => {
                if (this.selectedUser) {
                    router(`/profile`, { id: this.selectedUser });
                } else {
                    console.warn("No conversation selected. Unable to navigate to profile.");
                }
            });
        },

        removeAvatarClick() {
            const avatar = this.domManip.$id("chat-view-header-avatar");
            avatar.style.cursor = "default";
            avatar.removeEventListener("click", () => {});
        },

        populateConversationHeader() {
            let title;

            if (this.conversationParams.isGroupChat)
                title = translate("chat", "group");
            else{
                title = translate("chat", "subject");
                this.selectedUser = this.conversationParams.userId;
                console.log("Selected user:", this.selectedUser);
            }
            this.domManip.$id("chat-view-header-subject").textContent = title + this.conversationParams.conversationName;
            if (this.conversationParams.online)
                this.domManip.$id("chat-view-header-online-icon").src = "../assets/onlineIcon.png";
            else
                this.domManip.$id("chat-view-header-online-icon").src = "../assets/offlineIcon.png";
            this.domManip.$id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + this.conversationParams.conversationAvatar;
        },

        populateConversationMessages(data) {

            const container = this.domManip.$id("chat-view-messages-container");

            this.removeConversationMessages();
            // Reverse the data to display the messages in the correct order
            data.reverse();
            for (let element of data)
                createMessage(element, false, true);
        },

        removeConversationMessages() {
            let toDelete = this.domManip.$queryAll(".chat-view-sent-message-container, .chat-view-incoming-message-container, .chat-view-overlords-message-container, .spinner-grow")

            for (let element of toDelete)
                element.remove();
        },

        higlightCard(element) {

            let highlightedElement = this.domManip.$class("chat-view-conversation-card-highlighted");
            if (highlightedElement){
                for (let individualElement of highlightedElement)
                    individualElement.className = "chat-view-conversation-card";
            }
            element.className = "chat-view-conversation-card-highlighted";
        },

        conversationCallback(event) {

            let element = event.srcElement;
            let selectedConversationId = element.getAttribute("conversation_id");
            if (!selectedConversationId){
                element = event.srcElement.parentElement;
                selectedConversationId = element.getAttribute("conversation_id");
            }
            if (!selectedConversationId){
                console.error("No conversation_id found in conversationCallback");
                return ;
            }
            this.selectedConversation = selectedConversationId;
            this.higlightCard(element);
            this.loadConversation(selectedConversationId);
        },
        updateConversationUnreadCounter(conversationId, value) {
            let element = this.domManip.$id("chat-view-conversation-card-" +  conversationId);
            let unseenContainer = element.querySelector(".chat-view-conversation-card-unseen-container");
            if (value == 0)
                unseenContainer.style.display = "none";
            else {
                unseenContainer.style = "flex";
                unseenContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = value;
            }
        },
        loadConversation(conversationId) {
            call(`chat/load/conversation/${conversationId}/messages/?msgid=0`, 'PUT').then(data => {
                // Update badges
                this.domManip.$id("chat-nav-badge").textContent = data.totalUnreadCounter || "";
                this.updateConversationUnreadCounter(conversationId, data.conversationUnreadCounter);
                this.domManip.$id("chat-view-conversation-card-" +  conversationId).querySelector(".chat-view-conversation-card-unseen-counter").textContent = data.unreadCounter || "";
                if (data.data && data.data.length > 0) {
                    const temp = data.data.pop();
                    console.log("Last message:", temp);
                    this.lastMessageId = temp.id;
                    console.log("Last message id:", this.lastMessageId);
                    data.data.push(temp);
                } else {
                    console.warn("No messages returned in loadConversation");
                    if (this.lastMessageId == undefined){
                        this.lastMessageId = 0; // Fallback value
                    }
                }
                this.conversationParams = data;
                this.domManip.$id("chat-view-text-field").setAttribute("conversation-id", this.conversationParams.conversationId);
                this.populateConversationHeader();
                this.populateConversationMessages(data.data);
                WebSocketManager.setCurrentConversation(this.conversationParams.conversationId);
                this.showChatElements();
            });
        },

        createConversationCard(element) {

            console.log("element:", element);

            this.conversations.push(element.conversationId);

            const conversation = this.domManip.$id("chat-view-conversation-card-template").content.cloneNode(true);

            let container = conversation.querySelector(".chat-view-conversation-card");

            if (element.conversationId == this.routeParams.id)
                this.higlightCard(container);

            container.id = "chat-view-conversation-card-" +  element.conversationId;
            container.setAttribute("conversation_id", element.conversationId);
            container.setAttribute("last-message-time", element.lastUpdate);

            // Avatar
            conversation.querySelector(".chat-view-conversation-card-avatar").src = window.origin + '/media/avatars/' + element.conversationAvatar;

            // User
            conversation.querySelector(".chat-view-conversation-card-username").textContent = element.conversationName;

            // Seen container
            const unseenContainer = conversation.querySelector(".chat-view-conversation-card-unseen-container");
            if (element.unreadCounter == "0")
                unseenContainer.style.display = "none";
            else {
                unseenContainer.style = "flex";
                unseenContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = element.unreadCounter;
            }

            this.conversationsContainer.appendChild(conversation);
            this.domManip.$on(container, "click", this.conversationCallback);
        },

        populateConversations() {
            call('chat/load/conversations/', 'GET').then(data => {
                if (!data.data)
                {
                    this.domManip.$id("chat-view-conversations-no-converations-found").textContent = data.message;
                    return ;
                }

                for (let element of data.data)
                    this.createConversationCard(element);
            }).then(date => {

                this.sortConversationsByTimestamp();
            })
        },

        removeConversationsEventListners() {
            for (element of this.conversations)
                this.domManip.$off("chat-view-conversation-card-" +  element, "click", this.conversationCallback)
        },

        sortConversationsByTimestamp() {
            const conversationsContainer = this.domManip.$id('chat-view-conversations-container');

            const conversationCardsArray = Array.from(this.domManip.$queryAll(".chat-view-conversation-card, .chat-view-conversation-card-highlighted"));

            conversationCardsArray.sort((a, b) => {
                const timestampA = new Date(a.getAttribute('last-message-time'));
                const timestampB = new Date(b.getAttribute('last-message-time'));
                return timestampB - timestampA; // Sort in descending order (latest first)
            });

            conversationCardsArray.forEach(card => {
                conversationsContainer.appendChild(card);
            });
        },

        hideChatElements() {
            this.domManip.$id("chat-view-header-invite-for-game-image").style.display = "none";
            this.domManip.$id("chat-view-header-subject-container").style.display = "none";
            this.domManip.$id("chat-view-header-avatar").style.display = "none";
            this.domManip.$id("chat-view-text-field-container").style.display = "none";
        },

        showChatElements() {
            this.domManip.$id("chat-view-header-invite-for-game-image").style.display = "block";
            this.domManip.$id("chat-view-header-subject-container").style.display = "flex";
            this.domManip.$id("chat-view-header-avatar").style.display = "block";
            this.domManip.$id("chat-view-text-field-container").style.display = "block";
        },

    },

    hooks: {
        async beforeRouteEnter() {
            // await this.loadConversations();
        },

        beforeRouteLeave() {
			// TODO: Double check if this below is right an complete
            this.conversations = [];
            this.selectedConversation = null;
            this.removeInfiniteScroll();
            this.removeAvatarClick();
            //this.messages = [];

            WebSocketManager.setCurrentRoute(undefined);
            WebSocketManager.setCurrentConversation(undefined);

            this.removeConversationsEventListners();
        },

        beforeDomInsertion() {
			// TODO: Maybe check if the WebSocket is already open (which it should be from WebSocketManager)
        },

        // Open WebSocket after the DOM is inserted
        async afterDomInsertion() {
            WebSocketManager.setCurrentRoute("chat");
            this.conversationsContainer = this.domManip.$id("chat-view-conversations-container");
            this.hideChatElements();
            await this.populateConversations();
            this.initInfiniteScroll();
            this.initAvatarClick();

            if (this.routeParams?.id){
                console.log("this.routeParams.id:", this.routeParams.id);
                this.loadConversation(this.routeParams.id);
            }


            //          maybe the routeParam.id should be defined if no params are set.
            // TODO: issue #208 when params are not defined the routeParam.id crashes


			// Add event listener for the Send button
            // const sendButton = document.getElementById("chat-message-submit");
            // const messageInput = document.getElementById("chat-message-input");

            // if (sendButton && messageInput) {
            //     sendButton.onclick = () => {
            //         this.sendMessage(messageInput.value); // Send the message via WebSocket
            //         messageInput.value = ''; // Clear the input field
            //     };

            //     messageInput.onkeyup = (e) => {
            //         if (e.keyCode === 13) { // If "Enter" is pressed, send the message
            //             sendButton.click();
            //         }
            //     };
            // }
        },
    },
};

