
export default {
    attributes: {
		converations: [], // Array of all conversations
		selectedConversation: undefined, // The selected conversation
		messages: [], // Array of loaded conversion aka all messages; empty on start because no conversation is selected
    },

    methods: {
		// Load all conversations
		// this is calling an endpoint that returns all conversations as json
		// e.g. /chat/conversations
			// the user id is in the jwt token and will be fetched like this.$store.fromState(
		loadAllConversations() {
			// fetch all conversations
			// save them in this.conversations
		},

		// Select a conversation
		selectConversation(conversation) {
			// set this.selectedConversation to the selected conversation
			// load all messages of the selected conversation
			
		},

		// Load all messages of a conversation

		// Send a message to a conversation
    },

    hooks: {
        beforeRouteEnter() {
			// Load all conversations
			this.loadAllConversations();
        },

        beforeRouteLeave() {
			// Clear all attributes
			// Close (all) websocket connection(s)
        },

        beforeDomInsertion() {
			// open a websocket connection to the selected conversation
			// RAJH: one websocket client not per conversation!
			// TODO: check this
			// research about DOM manipulation !!!!
        },

        afterDomInsertion() {

        },
    }
}






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
