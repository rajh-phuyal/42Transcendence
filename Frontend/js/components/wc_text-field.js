import { createMessage } from '../views/chat/methods.js';
import { $id } from '../abstracts/dollars.js';
import $store from '../store/store.js';
import { translate } from '../locale/locale.js';
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
    }

    buttonclick(){
        const inputElement = this.shadow.getElementById("text-field");
        const value = inputElement.value;

        console.log("input value:", value);
        inputElement.value = '';
    }

    handleKeyPress(event){
        if (event.key !== 'Enter')
            return ;
        if (event.shiftKey)
            return ;
        event.preventDefault();
        const inputElement = event.target;
        const value = inputElement.value;
        console.log("input value:", value); // ...............................

        const container = $id("chat-view-messages-container");
        container.prepend(createMessage({"content": value, "createdAt": moment.utc().toISOString(), "userId": $store.fromState("user").id}));

        const toSend = {messageType: "chat", conversationId: this.conversationId, content: value};
        console.log("message", toSend)
        WebSocketManager.sendChatMessage(toSend);

        if (this.clear){
            inputElement.value = '';
        }
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
            console.log("convo id:", newValue)
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
                <button id="textFieldButton">Send</button>
            </div>
        `;
    }
}

customElements.define("text-field", TextField);


