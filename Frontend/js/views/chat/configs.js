
export default {
    attributes: {
        chatSocket: null, // WebSocket connection
        conversations: [], // All conversations for the user
        selectedConversation: null, // The active conversation
        messages: [], // Messages of the active conversation
    },

    methods: {
        // Load all conversations via API
        async loadConversations() {
            try {
                console.log('Bearer ' + this.$store.fromState('jwtTokens').access);
                // Use the abstracted call method instead of fetch
                const conversations_respond = await this.call('chat/conversations/', 'GET');

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

        // Open WebSocket connection
        openWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            //const socketUrl = `${protocol}${window.location.host}/ws/chat/`;
            const socketUrl = `ws://127.0.0.1:8000/ws/chat/`; //TODO: change later
            console.log("Opening WebSocket connection to", socketUrl);

            // Store the WebSocket connection
            this.chatSocket = new WebSocket(socketUrl);

            // Handle incoming messages from WebSocket
            this.chatSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log("WebSocket message received:", data);

                // If it's a chat message
                if (data.type === 'chat_message') {
                    // Add the new message to the chat log
                    this.messages.push(data.message);
                } else if (data.type === 'chat_messages') {
					// Handle receiving multiple messages (for conversation loading)
					this.messages = undefined;
                    this.messages = data.messages;
                }
				this.displayMessages();  // Function to update the UI

                // TODO: later
                // If it's a notification, you can handle it here too
                //if (data.type === 'notification') {
                //    console.log('Notification received:', data.content);
                //    // Handle notifications here
                //}
            };

            // Handle WebSocket closure
            this.chatSocket.onclose = (e) => {
                console.error("WebSocket connection closed unexpectedly");
            };
        },

        // Method to load messages when a conversation is selected
        async selectConversation(conversation) {
            console.log('Selected conversation:', conversation);
            this.selectedConversation = conversation;
        
            // Send a request to the backend to load messages for this conversatio
			console.log('Send a request to the backend to load messages for this conversation:', conversation.id);
            if (this.chatSocket) {
                this.chatSocket.send(JSON.stringify({
                    'type': 'load_messages',
                    'conversation_id': conversation.id
                }));
            }
        },

        // Send a chat message
        sendMessage(message) {
            if (this.chatSocket && message.trim() !== '') {
                // Prepare the message payload
                const payload = JSON.stringify({
                    type: 'chat_message',
                    message: message,
                });

                // Send the message through WebSocket
                this.chatSocket.send(payload);
                console.log("Message sent:", message);
            }
        },

        // Display messages in the chat log
        displayMessages() {
            const chatLog = document.getElementById("chat-log");
            chatLog.value = '';  // Clear previous content
			console.log(this.$store.fromState('user').id);
            this.messages.forEach(msg => {
				if (msg.sender === this.$store.fromState('user').id) {
                	chatLog.value += `                  ${msg.content}\n`;
				}
				else
                	chatLog.value += `${msg.sender}: ${msg.content}\n`;
            });
        }
    },

    hooks: {
        async beforeRouteEnter() {
            await this.loadConversations(); // Load all conversations when the chat is entered
        },

        beforeRouteLeave() {
            // Close WebSocket when leaving the chat view
            //if (this.chatSocket) {
            //    this.chatSocket.close();
            //}
            //this.chatSocket = null;
            this.conversations = [];
            this.selectedConversation = null;
            //this.messages = [];
        },

        beforeDomInsertion() {
            // This hook is invoked when the DOM is being created, before the insertion.
            console.log("Before DOM Insertion");
        },

        // Open WebSocket after the DOM is inserted
        afterDomInsertion() {
            console.log("After DOM Insertion: Opening WebSocket...");
            this.openWebSocket(); // Open the WebSocket connection

            // Add event listener for the Send button
            const sendButton = document.getElementById("chat-message-submit");
            const messageInput = document.getElementById("chat-message-input");

            if (sendButton && messageInput) {
                sendButton.onclick = () => {
                    this.sendMessage(messageInput.value); // Send the message via WebSocket
                    messageInput.value = ''; // Clear the input field
                };

                messageInput.onkeyup = (e) => {
                    if (e.keyCode === 13) { // If "Enter" is pressed, send the message
                        sendButton.click();
                    }
                };
            }
        },
    },
};