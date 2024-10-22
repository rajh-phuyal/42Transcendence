import $store from '../../store/store.js';  // Import the store

export default {
    hooks: {
        afterDomInsertion() {
            // Ensure the DOM is ready before adding event listeners
            const chatMessageInput = document.querySelector('#chat-message-input');
            const chatSubmitButton = document.querySelector('#chat-message-submit');
            const chatLog = document.querySelector('#chat-log');

            if (chatMessageInput && chatSubmitButton && chatLog) {
                // Retrieve the JWT token from the store
                const token = $store.fromState('jwtTokens').access;  // Get token from the store

                if (!token) {
                    console.error('JWT token is missing. Please log in.');
                    // Handle missing token (e.g., redirect to login)
                    return;
                }

                // WebSocket setup with JWT token in query string
                const roomName = "test-room";  // Static room name for now
                const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
                const chatSocket = new WebSocket(protocol + window.location.host + '/ws/chat/' + roomName + '/?token=' + token);


                chatSocket.onmessage = function(e) {
                    const data = JSON.parse(e.data);
                    chatLog.value += (data.message + '\n');
                };

                chatSocket.onclose = function(e) {
                    console.error('Chat socket closed unexpectedly');
                };

                chatMessageInput.onkeyup = function(e) {
                    if (e.keyCode === 13) {
                        chatSubmitButton.click();
                    }
                };

                chatSubmitButton.onclick = function(e) {
                    const message = chatMessageInput.value;
                    chatSocket.send(JSON.stringify({ 'message': message }));
                    chatMessageInput.value = '';
                };
            } else {
                console.error("Chat DOM elements not found!");
            }
        }
    }
};
