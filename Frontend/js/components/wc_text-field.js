import { createMessage, createHelpMessage, updateHelpMessage } from '../views/chat/methods.js';
import { $id, $queryAll } from '../abstracts/dollars.js';
import $store from '../store/store.js';
import { translate } from '../locale/locale.js';
import router from '../navigation/router.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';

class TextField extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.conversationId = undefined;
    }

    static get observedAttributes() {
        return ["placeholder", "width", "height", "clear", "conversation-id"];
    }

    focus() {
        this.shadow.getElementById("text-field").focus();
    }

    getInput() {
        return this.shadow.getElementById("text-field").value;
    }

    setEnabled(value) {
        let sendButton = this.shadow.getElementById("textFieldButton");
        if (value){
            sendButton.disabled = false;
        } else {
            sendButton.disabled = true;
        }
    }

    setInput(value) {
        this.shadow.getElementById("text-field").value = value;
        if(value.trim() !== ''){
            this.setEnabled(true);
        }
    }

    connectedCallback() {
        this.render();
        const inputElement = this.shadow.getElementById("textFieldButton");
        inputElement.addEventListener('click', this.buttonclick.bind(this));
        const inputElement2 = this.shadow.getElementById("text-field");
        inputElement2.addEventListener('keydown', this.handleKeyPress.bind(this));
        inputElement2.addEventListener('input', this.handleMessageInput.bind(this));
    }

    startSendingMessage(){
        const inputElement = this.shadow.getElementById("text-field");
        const value = inputElement.value.trim();
        if (value === '')
            return;
        // Reset text box & hide the help message when the user sends a message
        inputElement.value = '';
        this.setEnabled(false);
        updateHelpMessage();
        // Reset the template
        const highlightedCards = $queryAll(".chat-view-conversation-card-highlighted");
        highlightedCards[0].removeAttribute("message-draft");
        // Send the message to the server
        WebSocketManager.sendMessage({messageType: "chat", conversationId: this.conversationId, content: value});
        // If the message is a cmd we need to reload the view.
        // This is because the cmd might have changed the blocking state of the users
        const valueUpper = value.toUpperCase();
        if (valueUpper.startsWith("/B") || valueUpper.startsWith("/U")) {
            router('/chat', { id: this.conversationId });
        }
    }

    buttonclick(){
        this.startSendingMessage();
    }

    handleKeyPress(event){
        if(event.key === 'Escape') {
            $id("chat-view-searchbar").focus();
            return;
        }
        if (event.key !== 'Enter')
            return ;
        if (event.shiftKey)
            return ;
        event.preventDefault();
        this.startSendingMessage();
    }

    handleMessageInput(event){
        let sendButton = this.shadow.getElementById("textFieldButton");
        if (event.target.value.trim() === '')
            sendButton.disabled = true;
        else
            sendButton.disabled = false;
        createHelpMessage(event.target.value)
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "placeholder") {
            this.placeholder = newValue;
        }
        else if (name === "width") {
            this.width = newValue;
        }
        else if (name === "clear") {
            this.clear = true;
        }
        else if (name === "height") {
            this.height = newValue;
        }
        else if (name === "conversation-id") {
            //console.log("conversation id:", newValue)
            this.conversationId = newValue;
        }

        // this.render();
    }

    render() {
        this.shadow.innerHTML = `
            <div id="main-container">
                <textarea id="text-field" class="barely-a-scroll-class" type="search" maxlength="250" placeholder="${translate("chat", "textAreaPlaceHolder")}"></textarea>
                <button id="textFieldButton">${translate("chat", "sendButton")}</button>
            </div>
            <style>
                div {
                    color: black;
                    font-weight: 600;
                    width: 99% !important;
                    height: 100% !important;
                    align-items: center;
                    border:  0.5vh solid  black;
                    overflow: hidden;
                    background-color: #FFF7E3;
                }

                textarea {
                    font-size: min(1vw, 15px);
                    font-family: 'Courier';
                    color: black;

                    height: calc(100% - 0.5vh);

                    flex: 1;
                    overflow-y: auto;
                    border:  none;
                    border-radius: 3px;
                    outline: none;
                    background-color: #FFF7E3;
                    resize: none;

                }

                textarea:hover{
                    background-color: #EFE7D3;
                }

                textarea:focus{
                    background-color: #EFE7D3;
                }

                button {
                    margin: 0 0.5vw 0 0.5vw;
                    width: 12% !important;
                    height: 90% !important;
                    font-family: 'Courier';
                    font-size: min(1vw, 15px);
                    vertical-align: middle;
                    text-align: center;
                    align-items: justify;
                    font-weight: 700;
                    color: #FFFCE6;
                    background-color: #000000;
                    cursor: pointer;
                    /* margin: 20px 40px !important; */
                    border: 2px solid #968503;
                }

                button:hover {
                    background-color: #303030;
                }

                button:active{
                    background-color: #505050;
                }
                button:disabled,
                button[disabled]{
                    background-color:rgba(145, 143, 143, 0.9);
                }
                #main-container {
                    display: flex;
                    flex-direction: row;
                }

                /* Since the shadow dom can't read from main.css i need to copy this here: */
                .barely-a-scroll-class::-webkit-scrollbar {
                    width: 5px;
                }
                .barely-a-scroll-class::-webkit-scrollbar-thumb {
                    background-color: #727272;
                }
                .barely-a-scroll-class::-webkit-scrollbar-track {
                    background-color: black;
                }

            </style>
        `;
    }
}

customElements.define("text-field", TextField);


