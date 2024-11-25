import { createMessage } from '../views/chat/methods.js';
import { $id } from '../abstracts/dollars.js'

class TextField extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes() {
        return ["placeholder", "width", "height", "clear"];
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

    createTimestamp() {
        const date = new Date(); // Current date and time in local timezone
    
        // Extract date components
        const year = date.getUTCFullYear();
        const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
        const day = date.getUTCDate().toString().padStart(2, '0');
    
        // Extract time components
        const hours = date.getUTCHours().toString().padStart(2, '0');
        const minutes = date.getUTCMinutes().toString().padStart(2, '0');
        const seconds = date.getUTCSeconds().toString().padStart(2, '0');
    
        // Extract milliseconds and pad to 6 digits (convert to microseconds)
        const milliseconds = date.getUTCMilliseconds().toString().padStart(3, '0');
        const microseconds = `${milliseconds}000`;
    
        // UTC offset
        const utcOffset = "+00"; // Always UTC
    
        // Combine components into the desired format
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${microseconds}${utcOffset}`;
    }

    handleKeyPress(event){

        if (event.key !== 'Enter' || event.shiftKey)
            return ;
        event.preventDefault();
        const inputElement = event.target;
        const value = inputElement.value;
        console.log("input value:", value); // ...............................

        const container = $id("chat-view-messages-container");
        container.prepend(createMessage({"content": value, "createdAt": this.createTimestamp()}, true));

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
        this.render();
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
                <textarea id="text-field" type="search" maxlength="2000" placeholder="${this.placeholder || 'Search...'}"></textarea>
                <button id="textFieldButton">Send</button>
            </div>
        `;
    }
}

customElements.define("text-field", TextField);


