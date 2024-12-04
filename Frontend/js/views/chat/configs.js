import call from '../../abstracts/call.js';
import { translate } from '../../locale/locale.js';
import { createMessage } from './methods.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';

export default {
    attributes: {
        chatSocket: null, // WebSocket connection //TODO: not sure if we need this since we are using WebSocketManager
        conversations: [], // All conversations for the user
        selectedConversation: null, // The active conversation
        messages: [], // Messages of the active conversation

        conversationsContainer: undefined,
        conversations: [],
        conversationParams: undefined,
        lastMessageId: undefined,
    },

    methods: {

        alexCode() {
        // UNCOMENT FROM HERE++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        // // Load all conversations via API request (GET /chat/load/conversations)
        // async loadConversations() {
        //     try {
        //         console.log('Bearer ' + this.$store.fromState('jwtTokens').access);
        //         // Use the abstracted call method instead of fetch
        //         const conversations_respond = await this.call('chat/load/conversations/', 'GET');

        //         console.log("Conversations loaded:", conversations_respond);
                
        //     // Populate the conversation list UI
        //     const conversationListElement = document.getElementById("conversation-items");
        //     conversationListElement.innerHTML = ''; // Clear any existing items
                        
        //     conversations_respond.forEach(conversation => {
        //         const listItem = document.createElement('li');
        //         listItem.textContent = conversation.name || `Conversation ${conversation.id}`;
        //         listItem.setAttribute('data-id', conversation.id);
        //         listItem.style.cursor = 'pointer';
        //         listItem.addEventListener('click', () => {
        //             this.selectConversation(conversation); // Use the selectConversation method
        //         });
        //         conversationListElement.appendChild(listItem);
        //     });
                
        //     } catch (error) {
        //         console.error('Failed to load conversations:', error);
        //     }
        // },

		// // Load messages for the selected conversation
		// async selectConversation(conversation) {
        //     console.log('Selected conversation:', conversation, 'ID:', conversation.id);
        //     this.selectedConversation = conversation.id
        
		// 	try {
		// 		// Use the abstracted call method instead of fetch
		// 		//TODO: add offsett for pagination (change 0 in the next line)
		// 		const messages_respond = await this.call(`chat/load/conversation/${conversation.id}/messages/?offset=0/`, 'PUT');
		// 		console.log("Messages loaded:", messages_respond);

        //     // Populate the chat log with the messages
		// 	this.messages = messages_respond;
		// 	this.displayMessages();
		// 	} catch (error) {
		// 		console.error('Failed to load messages:', error);
		// 	}
        // },

		// // Display messages in the chat log
        // displayMessages() {
        //     const chatLog = document.getElementById("chat-log");
        //     chatLog.value = '';  // Clear previous content
		// 	console.log(this.$store.fromState('user').id);
        //     this.messages.forEach(msg => {
		// 		if (msg.user === this.$store.fromState('user').id) {
        //         	chatLog.value += `                                                        ${msg.content}\n`;
		// 		}
		// 		else
        //         	chatLog.value += `${msg.user}: ${msg.content}\n`;
        //     });
        // },

        // TO HERE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


// THIS IS OUTDATED SINCE WE ARE USING THE WebSocketManager
        // Open WebSocket connection
//        openWebSocket() {
//            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
//            //const socketUrl = `${protocol}${window.location.host}/ws/chat/`;
//            const socketUrl = `ws://127.0.0.1:8000/ws/chat/?token=${this.$store.fromState('jwtTokens').access}`; //TODO: change later
//            console.log("Opening WebSocket connection to", socketUrl);
//
//            // Store the WebSocket connection
//            this.chatSocket = new WebSocket(socketUrl);
//
//            // Handle incoming messages from WebSocket
//            this.chatSocket.onmessage = (event) => {
//                const data = JSON.parse(event.data);
//                console.log("WebSocket message received:", data);
//
//                // If it's a chat message
//                if (data.type === 'chat_message') {
//                    // Add the new message to the chat log
//					if (data.conversation_id === this.selectedConversationId) {
//						// Push the new message to the messages array
//                    	this.messages.push(data.message);
//					}
//					else {
//						// TODO: later
//						// Add a notification for the new message
//						console.log('New message received in another conversation:', data.message);
//					}
//                } else if (data.type === 'chat_messages') {
//					// Handle receiving multiple messages (for conversation loading)
//					this.messages = undefined;
//                    this.messages = data.messages;
//                }
//				this.displayMessages();  // Function to update the UI
//
//                // TODO: later
//                // If it's a notification, you can handle it here too
//                //if (data.type === 'notification') {
//                //    console.log('Notification received:', data.content);
//                //    // Handle notifications here
//                //}
//            };
//
//            // Handle WebSocket closure
//            this.chatSocket.onclose = (e) => {
//                console.error("WebSocket connection closed unexpectedly");
//            };
//        },


        // Method to load messages when a conversation is selected

		
        // UNCOMENT THIS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        // Send a chat message
        // sendMessage(message) {
        //     if (this.chatSocket && message.trim() !== '') {
        //         // Prepare the message payload
        //         const payload = JSON.stringify({
        //             type: 'chat_message',
        //             message: message,
		// 			conversation_id: this.selectedConversation,
        //         });

        //         // Send the message through WebSocket
        //         this.chatSocket.send(payload);
        //         console.log("Message sent:", message + 'to conversation: ' + this.selectedConversation);
        //     }
        // },
        },

        populateConversationHeader() {
            let title;

            if (this.conversationParams.isGroupChat)
                title = translate("chat", "group");
            else
                title = translate("chat", "subject");
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
            
            for (let element of data) 
                container.appendChild(createMessage(element));
        },
        
        removeConversationMessages() {
            let toDelete = this.domManip.$queryAll(".chat-view-sent-message-container, .chat-view-incoming-message-container, .chat-view-overlords-message-container")
    
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

            if (!element.getAttribute("conversation_id"))
                element = event.srcElement.parentElement;

            this.higlightCard(element);
            this.loadConversation(element.getAttribute("conversation_id"));
        },
        loadConversation(conversationId) {
            call(`chat/load/conversation/${conversationId}/messages/?msgid=0`, 'PUT').then(data => {
                const temp = data.data.pop();
                this.lastMessageId= temp.messageId;
                data.data.push(temp);
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

        async populateConversations() {
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

            // TODO: when params are not defined the routeParam.id crashes
            //          maybe the routeParam.id should be defined if no params are set.
            WebSocketManager.setCurrentRoute("chat");
            this.hideChatElements();
            if (this.routeParams.id)
                this.loadConversation(this.routeParams.id);
            this.conversationsContainer = this.domManip.$id("chat-view-conversations-container");

            await this.populateConversations();
            

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
