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
        const value = inputElement.value;
        // Reset text box & hide the help message when the user sends a message
        inputElement.value = '';
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
            <style>
                div {
                    color: black;
                    font-weight: 600;
                    width: ${this.width || '20'}%;
                    height: ${this.height || '20'}%;
                    align-items: center;
                    flex: 1;
                    padding: 5px;
                    border:  3px solid  black;
                    outline: none;
                    background-color: #FFF7E3;
                }

                textarea {
                    font-size: 16px;
                    font-family: 'Courier';
                    color: black;
                    width: 50%;
                    height: 100%;
                    font-weight: 600;
                    flex: 1;
                    padding: 5px;
                    border:  none;
                    border-radius: 3px;
                    outline: none;
                    background-color: #FFF7E3;
                    resize: none;
                    overflow: auto;
                }

                textarea:hover{
                    background-color: #EFE7D3;
                }

                textarea:focus{
                    background-color: #EFE7D3;
                }

                button {
                    font-family: 'Courier';
                    font-size: 16px;
                    font-weight: 700;
                    margin: 5% 0% 0% 0%;
                    width: 12%;
                    height: 40%;
                    border: 3px solid  black;
                    cursor: pointer;
                    background-color: black;
                    color: white;
                }

                button:hover {
                    background-color: #303030;
                }

                button:active{
                    background-color: #505050;
                }
                #main-container {
                    display: flex;
                    flex-direction: row;
                }
            </style>
            <div id="main-container">
                <textarea id="text-field" type="search" maxlength="250" placeholder="${translate("chat", "textAreaPlaceHolder")}"></textarea>
                <button id="textFieldButton">${translate("chat", "sendButton")}</button>
            </div>
        `;
    }
}

customElements.define("text-field", TextField);


