import call from '../../abstracts/call.js';
import { translate } from '../../locale/locale.js';
import { createMessage } from './methods.js';
import { createConversationCard } from "./methods.js";
import { updateConversationUnreadCounter, selectConversation, createLoadingSpinner, resetConversationView, loadMessages } from './methods.js';
import router from '../../navigation/router.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import $store from '../../store/store.js';

/* QUICK EXPLANATION:
    Where is what stored?
    - Selected conversation id:
        .$id("chat-view-text-field").getAttribute("conversation-id")
    - Selected conversation user id:
        .$id("chat-view-header-avatar").getAttribute("user-id");
    - Last message id of currenty loaded conversation:
        .$id("chat-view-messages-container").getAttribute("last-message-id");
*/

export default {
    attributes: {
    },

    methods: {
        initInfiniteScroll() {
            const container = this.domManip.$id("chat-view-messages-container");
            this.handleScroll = () => {
                console.log("Scrolling... %s/%s/%s", container.scrollTop, container.scrollHeight, container.clientHeight);
                if (container.scrollTop === 0) {
                    const conversationId = this.domManip.$id("chat-view-text-field").getAttribute("conversation-id");
                    if(conversationId){
                        const container = this.domManip.$id("chat-view-messages-container");
                        const lastMessageId = container.getAttribute("last-message-id");
                        const lastMessageContainer = this.domManip.$id("message-" + lastMessageId);
                        console.log("Last message id:", lastMessageContainer);
                        //let previousScrollPercent = container.scrollHeight > container.clientHeight
                        //    ? container.scrollTop / (container.scrollHeight - container.clientHeight)
                        //    : 0;
//
//                        loadMessages(conversationId)
                        loadMessages(conversationId).then(() => {
                            if (lastMessageContainer){
                                lastMessageContainer.scrollIntoView({
                                    behavior: "instant",
                                    block: "start",
                                });
                            }
                        }).catch(error => {
                            console.error("Failed to load messages during infinite scroll:", error);
                        });
                       //    const newScrollHeight = container.scrollHeight;
                        //    container.scrollTop = newScrollHeight > container.clientHeight
                        //        ? newScrollHeight * previousScrollPercent
                        //        : 0;
                        //    console.warn("Scrolling to", container.scrollTop);





//// If adjusting scroll, calculate the scroll position before adding the message
/// Manage the scroll position
// if (scrollToBottom){
//    container.scrollTop = container.scrollHeight + container.clientHeight;
//}
//else {
//    // Restore the user's scroll position
//    console.log("Scrolling to", previousScrollTop + (container.scrollHeight - previousScrollHeight));
//
//
//}








                    }
                    else
                        console.error("No conversation selected. Unable to load older messages.");
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
                const avatarElement = this.domManip.$id("chat-view-header-avatar");
                const userId = avatarElement.getAttribute("user-id");
                if (userId) {
                    router(`/profile`, { id: userId });
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

//        populateConversationHeader() {
//            let title;
//
//            if (this.conversationParams.isGroupChat)
//                title = translate("chat", "group");
//            else{
//                title = translate("chat", "subject");
//                this.selectedUserId = this.conversationParams.userId;
//                console.log("Selected user:", this.selectedUserId);
//            }
//            this.domManip.$id("chat-view-header-subject").textContent = title + this.conversationParams.conversationName;
//            if (this.conversationParams.online)
//                this.domManip.$id("chat-view-header-online-icon").src = "../assets/onlineIcon.png";
//            else
//                this.domManip.$id("chat-view-header-online-icon").src = "../assets/offlineIcon.png";
//            this.domManip.$id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + this.conversationParams.conversationAvatar;
//        },

//        populateConversationMessages(data) {
//
//            const container = this.domManip.$id("chat-view-messages-container");
//
//            this.removeConversationMessages();
//            // Reverse the data to display the messages in the correct order
//
//        },

//        removeConversationMessages() {
//            let toDelete = this.domManip.$queryAll(".chat-view-sent-message-container, .chat-view-incoming-message-container, .chat-view-overlords-message-container, .spinner-grow")
//
//            for (let element of toDelete)
//                element.remove();
//        },

//        higlightCard() {
//            const allConversationCards = this.domManip.$queryAll(".chat-view-conversation-card, .chat-view-conversation-card-highlighted");
//            for (let element of allConversationCards){
//                if (element.getAttribute("conversation_id") == this.selectedConversationId){
//                    element.className = "chat-view-conversation-card-highlighted";
//                }else{
//                    element.className = "chat-view-conversation-card";
//                }
//            }
//        },

//        async conversationCallback(event) {
//            // Get the right html element
//            let element = event.srcElement;
//            let selectedConversationId = element.getAttribute("conversation_id");
//            if (!selectedConversationId){
//                element = event.srcElement.parentElement;
//                selectedConversationId = element.getAttribute("conversation_id");
//            }
//            if (!selectedConversationId){
//                console.error("No conversation_id found in conversationCallback");
//                return ;
//            }
//
//            // Set the current conversation
//            selectConversation(selectedConversationId);
//            return;
//            WebSocketManager.setCurrentConversation(this.selectedConversationId);
//            this.domManip.$id("chat-view-text-field").setAttribute("conversation-id", this.selectedConversationId);
//            console.log("Selected conversation:", this.selectedConversationId);
//
//            // Highlight the selected conversation card
//            this.higlightCard(element);
//
//            // Remove all Messages from conversation
//            this.removeConversationMessages();
//
//            // Load all messages from conversation and update lastMessageId
//            this.lastMessageId = 0;
//            await this.loadMessages(false, false, true);
//
//            // Show the chat elements
//            this.showChatElements();
//        },

//        async loadMessages(prepend = false, adjustScroll = true, scrollToBottom = false) {
//            if (this.isLoadingMessages){
//                console.warn("Already loading messages. Please wait.");
//                return ;
//            }
//            this.isLoadingMessages = true;
//
//            const spinner = createLoadingSpinner();
//            this.messagesContainer.prepend(spinner);
//            const startTime = Date.now();
//            const data = await call(`chat/load/conversation/${this.selectedConversationId}/messages/?msgid=${this.lastMessageId}`, 'PUT')
//            const elapsedTime = Date.now() - startTime;
//            const delay = Math.max(500 - elapsedTime, 0);
//
//            setTimeout(() => {
//                spinner.remove();
//
//                // Check if there are any messages
//                if (data.data && data.data.length > 0) {
//                    const temp = data.data.pop();
//                    console.log("Last message:", temp);
//                    this.lastMessageId = temp.id;
//                    console.log("Last message id:", this.lastMessageId);
//                    data.data.push(temp);
//                } else {
//                    console.warn("No messages returned in loadConversation");
//                    if (this.lastMessageId == undefined){
//                        this.lastMessageId = 0; // Fallback value
//                    }
//                }
//
//                // Update badges
//                this.domManip.$id("chat-nav-badge").textContent = data.totalUnreadCounter || "";
//                updateConversationUnreadCounter(this.selectedConversationId, data.conversationUnreadCounter);
//                this.domManip.$id("chat-view-conversation-card-" +  this.selectedConversationId).querySelector(".chat-view-conversation-card-unseen-counter").textContent = data.unreadCounter || "";
//
//                // STEP1: Update about Conversation section
//                // Update Title
//                let title;
//                title = translate("chat", "subject: ") + data.conversationName;
//                this.domManip.$id("chat-view-header-subject").textContent = title;
//
//                // Update online status
//                if (data.online)
//                    this.domManip.$id("chat-view-header-online-icon").src = "../assets/onlineIcon.png";
//                else
//                    this.domManip.$id("chat-view-header-online-icon").src = "../assets/offlineIcon.png";
//
//                // Update Avatar
//                this.domManip.$id("chat-view-header-avatar").src = window.origin + '/media/avatars/' + data.conversationAvatar;
//
//                // Update user id
//                this.selectedUserId = data.userId;
//
//                // STEP2: Load messages
//                data.data.reverse();
//                for (let element of data.data)
//                    createMessage(element, prepend, adjustScroll, scrollToBottom);
//
//            }, delay);
//            this.isLoadingMessages = false;
//        },
//
//        createConversationCard(element) {
//
//            console.log("element:", element);
//
//            this.conversations.push(element.conversationId);
//
//            const conversation = this.domManip.$id("chat-view-conversation-card-template").content.cloneNode(true);
//
//            let container = conversation.querySelector(".chat-view-conversation-card");
//
//            if (element.conversationId == this.routeParams.id)
//                this.higlightCard(container);
//
//            container.id = "chat-view-conversation-card-" +  element.conversationId;
//            container.setAttribute("conversation_id", element.conversationId);
//            container.setAttribute("last-message-time", element.lastUpdate);
//
//            // Avatar
//            conversation.querySelector(".chat-view-conversation-card-avatar").src = window.origin + '/media/avatars/' + element.conversationAvatar;
//
//            // User
//            conversation.querySelector(".chat-view-conversation-card-username").textContent = element.conversationName;
//
//            // Seen container
//            const unseenContainer = conversation.querySelector(".chat-view-conversation-card-unseen-container");
//            if (element.unreadCounter == "0")
//                unseenContainer.style.display = "none";
//            else {
//                unseenContainer.style = "flex";
//                unseenContainer.querySelector(".chat-view-conversation-card-unseen-counter").textContent = element.unreadCounter;
//            }
//
//            this.conversationsContainer.appendChild(conversation);
//            this.domManip.$on(container, "click", this.conversationCallback);
//        },

        async loadConversations() {
            // Set Vars
            const conversationsContainer = this.domManip.$id('chat-view-conversations-container');
            if(conversationsContainer.getAttribute("loading") == "true"){
                console.warn("Already loading conversations. Please wait.");
                return Promise.resolve();
            }

            conversationsContainer.setAttribute("loading", "true");

            // Remove all conversation cards
            let toDelete = this.domManip.$queryAll(".chat-view-sent-message-container, .chat-view-incoming-message-container, .chat-view-overlords-message-container, .spinner-grow")
            for (let element of toDelete)
                element.remove();

            // Show Spinner
            const spinner = createLoadingSpinner();
            conversationsContainer.prepend(spinner);
            const startTime = Date.now();

            // Load the conversations
            return call('chat/load/conversations/', 'GET')
                .then(data => {
                    //console.log('Data:', data);
                    const elapsedTime = Date.now() - startTime;
                    const delay = Math.max(200 - elapsedTime, 0);

                    return new Promise(resolve => {
                        setTimeout(() => {
                            spinner.remove();

                            // Check if there are any messages
                            if (!data.data) {
                                this.domManip.$id("chat-view-conversations-no-converations-found").textContent = data.message;
                                conversationsContainer.setAttribute("loading", "false");
                                resolve();
                                return;
                            }

                            // Create the conversation cards
                            for (let element of data.data) {
                                createConversationCard(element, false);
                            }

                            conversationsContainer.setAttribute("loading", "false");
                            resolve();
                        }, delay);
                    });
                })
                .catch(error => {
                    spinner.remove();
                    conversationsContainer.setAttribute("loading", "false");
                    console.error('Error occurred:', error);
                });
        },

        removeConversationsEventListners() {
            const allConversationCards = this.domManip.$queryAll(".chat-view-conversation-card, .chat-view-conversation-card-highlighted");
            //for (let element of allConversationCards)
                //TODO:this.domManip.$off("chat-view-conversation-card-" +  element, "click", this.conversationCallback)
        }
    },

//        sortConversationsByTimestamp() {
//            const conversationsContainer = this.domManip.$id('chat-view-conversations-container');
//
//            const conversationCardsArray = Array.from(this.domManip.$queryAll(".chat-view-conversation-card, .chat-view-conversation-card-highlighted"));
//
//            conversationCardsArray.sort((a, b) => {
//                const timestampA = new Date(a.getAttribute('last-message-time'));
//                const timestampB = new Date(b.getAttribute('last-message-time'));
//                return timestampB - timestampA; // Sort in descending order (latest first)
//            });
//
//            conversationCardsArray.forEach(card => {
//                conversationsContainer.appendChild(card);
//            });
//        },
//
//        hideChatElements() {
//            this.domManip.$id("chat-view-header-invite-for-game-image").style.display = "none";
//            this.domManip.$id("chat-view-header-subject-container").style.display = "none";
//            this.domManip.$id("chat-view-header-avatar").style.display = "none";
//            this.domManip.$id("chat-view-text-field-container").style.display = "none";
//        },
//
//        showChatElements() {
//            this.domManip.$id("chat-view-header-invite-for-game-image").style.display = "block";
//            this.domManip.$id("chat-view-header-subject-container").style.display = "flex";
//            this.domManip.$id("chat-view-header-avatar").style.display = "block";
//            this.domManip.$id("chat-view-text-field-container").style.display = "block";
//        },
//
//

    hooks: {
        async beforeRouteEnter() {
        },

        beforeRouteLeave() {
			// TODO: Double check if this below is right an complete
            this.conversations = [];
            this.selectedConversationId = null;
            this.removeInfiniteScroll();
            this.removeAvatarClick();
            //this.messages = [];

            WebSocketManager.setCurrentRoute(undefined);
            WebSocketManager.setCurrentConversation(undefined);

            this.removeConversationsEventListners();
        },

        beforeDomInsertion() {
        },

        async afterDomInsertion() {
            // Hide non MVP Elements
            this.domManip.$id("chat-view-header-invite-for-game-image").style.display = "none";
            this.domManip.$id("chat-view-header-group-chat-image").style.display = "none";

            WebSocketManager.setCurrentRoute("chat");
            // Init everything conversation related
            resetConversationView();
            // Init all variables we use later on:
            this.domManip.$id("chat-view-text-field").setAttribute("conversation-id", undefined);
            this.domManip.$id('chat-view-conversations-container').setAttribute("loading", "false");
            this.domManip.$id("chat-view-messages-container").setAttribute("loading", "false");

            // Load the conversations
            this.loadConversations()
                .then(() => {
                    if (this.routeParams?.id){
                        // Check if is is number
                        if (isNaN(this.routeParams.id)){
                            console.warn("Invalid conversation id '%s' from routeParams?.id will be ignored!", this.routeParams.id);
                            return ;
                        }
                        console.log("this.routeParams.id:", this.routeParams.id);
                        selectConversation(this.routeParams.id);
                    }
                })
                .catch(error => {
                    console.error("Error loading conversations:", error);
                });


            // Add event listeners
            this.initInfiniteScroll();
            this.initAvatarClick();
            // this.initSearch(); TODO



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