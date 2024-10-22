// configs.js for chat view

export default {
    attributes: {
        // You can add any custom attributes here if needed
    },
    
    methods: {
        // If you need to define reusable methods, add them here
    },
    
    hooks: {
        beforeRouteEnter() {
            // Runs when entering the chat route, initialize WebSocket here

            const roomName = "test-room";  // Static room name for now
            const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/chat/' + roomName + '/');

            chatSocket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                // Append the received message to the chat log
                document.querySelector('#chat-log').value += (data.message + '\n');
            };

            chatSocket.onclose = function(e) {
                console.error('Chat socket closed unexpectedly');
            };

            // When user presses the enter key or clicks 'Send', send the message
            document.querySelector('#chat-message-input').onkeyup = function(e) {
                if (e.keyCode === 13) {  // Enter key pressed
                    document.querySelector('#chat-message-submit').click();
                }
            };

            document.querySelector('#chat-message-submit').onclick = function(e) {
                const messageInputDom = document.querySelector('#chat-message-input');
                const message = messageInputDom.value;

                // Send the message through WebSocket
                chatSocket.send(JSON.stringify({
                    'message': message
                }));
                // Clear the input field
                messageInputDom.value = '';
            };
        },
        
        beforeRouteLeave() {
            // If you want to clean up before leaving the chat route
        },

        beforeDomInsertion() {
            // If there's anything you want to do before the DOM is rendered
        },

        afterDomInsertion() {
            // Anything to do after the DOM is fully rendered and interactive
        },
    },
};
