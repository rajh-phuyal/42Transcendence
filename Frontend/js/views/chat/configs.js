

export default {
    attributes: {
        chatSocket: null, // WebSocket connection //TODO: not sure if we need this since we are using WebSocketManager
        conversations: [], // All conversations for the user
        selectedConversation: null, // The active conversation
        messages: [], // Messages of the active conversation
    },

    methods: {
        // Load all conversations via API request (GET /chat/load/conversations)
        async loadConversations() {
            try {
                // TODO: this won't work since we have jwts in HTTP only cookies
                console.log('Bearer ' + this.$store.fromState('jwtTokens').access);
                // Use the abstracted call method instead of fetch
                const conversations_respond = await this.call('chat/load/conversations/', 'GET');

                console.log("Conversations loaded:", conversations_respond);

            // Populate the conversation list UI
            const conversationListElement = document.getElementById("conversation-items");
            conversationListElement.innerHTML = ''; // Clear any existing items

            conversations_respond.forEach(conversation => {
                const listItem = document.createElement('li');
                listItem.textContent = conversation.name || `Conversation ${conversation.id}`;
                listItem.setAttribute('data-id', conversation.id);
                listItem.style.cursor = 'pointer';
                listItem.addEventListener('click', () => {
                    this.selectConversation(conversation); // Use the selectConversation method
                });
                conversationListElement.appendChild(listItem);
            });

            } catch (error) {
                console.error('Failed to load conversations:', error);
            }
        },

		// Load messages for the selected conversation
		async selectConversation(conversation) {
            console.log('Selected conversation:', conversation, 'ID:', conversation.id);
            this.selectedConversation = conversation.id

			try {
				// Use the abstracted call method instead of fetch
				//TODO: add offsett for pagination (change 0 in the next line)
				const messages_respond = await this.call(`chat/load/conversation/${conversation.id}/messages/?offset=0/`, 'PUT');
				console.log("Messages loaded:", messages_respond);

            // Populate the chat log with the messages
			this.messages = messages_respond;
			this.displayMessages();
			} catch (error) {
				console.error('Failed to load messages:', error);
			}
        },

		// Display messages in the chat log
        displayMessages() {
            const chatLog = document.getElementById("chat-log");
            chatLog.value = '';  // Clear previous content
			console.log(this.$store.fromState('user').id);
            this.messages.forEach(msg => {
				if (msg.user === this.$store.fromState('user').id) {
                	chatLog.value += `                                                        ${msg.content}\n`;
				}
				else
                	chatLog.value += `${msg.user}: ${msg.content}\n`;
            });
        },

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



        // Send a chat message
        sendMessage(message) {
            if (this.chatSocket && message.trim() !== '') {
                // Prepare the message payload
                const payload = JSON.stringify({
                    type: 'chat_message',
                    message: message,
					conversation_id: this.selectedConversation,
                });

                // Send the message through WebSocket
                this.chatSocket.send(payload);
                console.log("Message sent:", message + 'to conversation: ' + this.selectedConversation);
            }
        },


    },

    hooks: {
        async beforeRouteEnter() {
            await this.loadConversations();
        },

        beforeRouteLeave() {
			// TODO: Double check if this below is right an complete
            this.conversations = [];
            this.selectedConversation = null;
            //this.messages = [];
        },

        beforeDomInsertion() {
            console.log("Before DOM Insertion");
			// TODO: Maybe check if the WebSocket is already open (which it should be from WebSocketManager)
        },

        // Open WebSocket after the DOM is inserted
        afterDomInsertion() {
            console.log("After DOM Insertion...");

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