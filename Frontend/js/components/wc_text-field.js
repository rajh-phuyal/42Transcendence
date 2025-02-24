import { createMessage, createHelpMessage, updateHelpMessage } from '../views/chat/methods.js';
import { $id } from '../abstracts/dollars.js';
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

    connectedCallback() {
        this.render();
        const inputElement = this.shadow.getElementById("textFieldButton");
        inputElement.addEventListener('click', this.buttonclick.bind(this));
        const inputElement2 = this.shadow.getElementById("text-field");
        inputElement2.addEventListener('keypress', this.handleKeyPress.bind(this));
        inputElement2.addEventListener('input', this.handleMessageInput.bind(this));
    }

    startSendingMessage(){
        const inputElement = this.shadow.getElementById("text-field");
        const value = inputElement.value.trim();
        if (value === '')
            return;
        // Reset text box & hide the help message when the user sends a message
        inputElement.value = '';
        let sendButton = this.shadow.getElementById("textFieldButton");
        sendButton.disabled = true;
        updateHelpMessage();
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
                <textarea id="text-field" type="search" maxlength="250" placeholder="${translate("chat", "textAreaPlaceHolder")}"></textarea>
                <button id="textFieldButton">${translate("chat", "sendButton")}</button>
            </div>
            <style>
                div {
                    color: black;
                    font-weight: 600;
                    width: 100% !important;
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
                    margin: 0 0.2vw 0 0;
                    width: 12% !important;
                    height: 90% !important;
                    font-family: 'Courier';
                    font-size: ${this.fontSize}vh;
                    vertical-align: middle;
                    text-align: center;
                    align-items: justify;
                    font-weight: 700;
                    color: #FFFCE6;
                    background-color: #000000;
                    cursor: pointer;
                    padding: 2px 4px !important;
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
            </style>
        `;
    }
}

customElements.define("text-field", TextField);


