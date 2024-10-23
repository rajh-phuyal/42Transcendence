
export default {
    attributes: {
		conversations: [], // All conversations for the user
        selectedConversation: null, // The active conversation
        messages: [], // Messages of the active conversation
    },

    methods: {
		// Load all conversations via API
		async loadConversations() {
			try {
				const response = await fetch('/chat/conversations/', {
					headers: {
						'Authorization': 'Bearer ' + this.getJWTToken()  // Replace this logic with your own token retrieval method
					}
				});
		
				if (!response.ok) {
					throw new Error('Failed to load conversations');
				}
		
				const conversations = await response.json();
		
				// Assuming you want to store the conversations in the 'conversations' attribute
				this.conversations = conversations;
		
				// Populate the conversation list dynamically in the DOM
				const conversationListElement = document.getElementById('conversation-items');
				conversationListElement.innerHTML = '';  // Clear previous content
		
				conversations.forEach(conversation => {
					const listItem = document.createElement('li');
					listItem.textContent = conversation.name || `Conversation ${conversation.id}`;
					listItem.setAttribute('data-id', conversation.id);
					listItem.style.cursor = 'pointer';
					listItem.addEventListener('click', () => this.selectConversation(conversation));
					conversationListElement.appendChild(listItem);
				});
		
			} catch (error) {
				console.error('Failed to load conversations:', error);
			}
		},

        // Select a conversation
        async selectConversation(conversation) {
            this.selectedConversation = conversation;
            this.messages = []; // Clear old messages
            await this.loadMessages(conversation.id); // Load messages for the selected conversation

            // After selecting conversation, open WebSocket
            this.openWebSocket(conversation.id);
        },

        // Load all messages of the selected conversation
        async loadMessages(conversationId) {
            try {
                const response = await fetch(`/chat/messages/${conversationId}`);
                this.messages = await response.json();
            } catch (error) {
                console.error('Failed to load messages:', error);
            }
        },

        // Open a single WebSocket connection
        openWebSocket(conversationId) {
            // Close previous WebSocket if any
            if (this.chatSocket) {
                this.chatSocket.close();
            }

            const token = $store.fromState('jwtTokens').access;
            const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            this.chatSocket = new WebSocket(`${protocol}${window.location.host}/ws/chat/${conversationId}/?token=${token}`);

            this.chatSocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.messages.push(data.message); // Add new message to the chat log
            };

            this.chatSocket.onclose = (event) => {
                console.error('Chat WebSocket closed unexpectedly.');
            };
        },

        // Send a message
        sendMessage(message) {
            if (this.chatSocket && message.trim() !== '') {
                this.chatSocket.send(JSON.stringify({ message }));
            }
        },
    },

    hooks: {
        async beforeRouteEnter() {
            await this.loadAllConversations(); // Load all conversations when the chat is entered
        },

        beforeRouteLeave() {
            // Close WebSocket when leaving the chat view
            if (this.chatSocket) {
                this.chatSocket.close();
            }
            this.chatSocket = null;
            this.selectedConversation = null;
            this.messages = [];
        },

        beforeDomInsertion() {
            // This hook is invoked when the DOM is being created, before the insertion.
            console.log("Before DOM Insertion");
        },

        afterDomInsertion() {
            // Add DOM event listeners after the view is inserted
            const sendButton = document.getElementById("chat-message-submit");
            const messageInput = document.getElementById("chat-message-input");

            if (sendButton && messageInput) {
                sendButton.onclick = () => {
                    this.sendMessage(messageInput.value);
                    messageInput.value = '';
                };

                messageInput.onkeyup = (e) => {
                    if (e.keyCode === 13) { // Enter key sends the message
                        sendButton.click();
                    }
                };
            }
        },
    },
};





// OLD BELOW
// -----------------------------------------------------------------------------

// import $store from '../../store/store.js';  // Import the store #TODO: this.$store is better!

// export default {
//     hooks: {
//         afterDomInsertion() {
//             // Ensure the DOM is ready before adding event listeners
//             const chatMessageInput = document.querySelector('#chat-message-input');
//             const chatSubmitButton = document.querySelector('#chat-message-submit');
//             const chatLog = document.querySelector('#chat-log');

//             if (chatMessageInput && chatSubmitButton && chatLog) {
//                 // Retrieve the JWT token from the store
//                 const token = $store.fromState('jwtTokens').access;  // Get token from the store

//                 if (!token) {
//                     console.error('JWT token is missing. Please log in.');
//                     // Handle missing token (e.g., redirect to login)
//                     return;
//                 }

//                 // WebSocket setup with JWT token in query string
// 				// TODO: Extract the websocket setup into a separate function to handel all websocket connections we have
//                 const roomName = "test-room";  // Static room name for now
//                 const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
//                 const chatSocket = new WebSocket(protocol + window.location.host + '/ws/chat/' + roomName + '/?token=' + token);


//                 chatSocket.onmessage = function(e) {
//                     const data = JSON.parse(e.data);
//                     chatLog.value += (data.message + '\n');
//                 };

//                 chatSocket.onclose = function(e) {
//                     console.error('Chat socket closed unexpectedly');
//                 };

//                 chatMessageInput.onkeyup = function(e) {
//                     if (e.keyCode === 13) {
//                         chatSubmitButton.click();
//                     }
//                 };

//                 chatSubmitButton.onclick = function(e) {
//                     const message = chatMessageInput.value;
//                     chatSocket.send(JSON.stringify({ 'message': message }));
//                     chatMessageInput.value = '';
//                 };
//             } else {
//                 console.error("Chat DOM elements not found!");
//             }
//         }
//     }
// };
