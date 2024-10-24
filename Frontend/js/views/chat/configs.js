
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

        // Placeholder for selecting a conversation
        async selectConversation(conversation) {
            console.log('Selected conversation:', conversation);
            // Additional logic to load messages for the conversation can be added later
        },

        // Other methods...

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

        afterDomInsertion() {
            // Add DOM event listeners after the view is inserted
			console.log("After DOM Insertion");
//			const sendButton = document.getElementById("chat-message-submit");
//			const messageInput = document.getElementById("chat-message-input");
//			
//			if (sendButton && messageInput) {
//			    sendButton.onclick = () => {
//			        this.sendMessage(messageInput.value);
//			        messageInput.value = '';
//			    };
//			
//			    messageInput.onkeyup = (e) => {
//			        if (e.keyCode === 13) { // Enter key sends the message
//			            sendButton.click();
//			        }
//			    };
//			}
        },
    },
};