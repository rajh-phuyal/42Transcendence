class TextField extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes() {
        return ["placeholder", "width", "clear"];
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

        if (event.key !== 'Enter' || event.shiftKey)
            return ;
        event.preventDefault();
        const inputElement = event.target;
        const value = inputElement.value;
        console.log("input value:", value);

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
        this.render();
    }

    render() {
        this.shadow.innerHTML = `
            <style>
                div {
                    color: black;
                    font-weight: 600;
                    width: ${this.width || '150'}px;
                    hight: 50;
                    align-items: center;
                    flex: 1;
                    padding: 5px;
                    border:  2px solid  #595959;
                    border-radius: 3px;
                    outline: none;
                    background-color: #FFF6D4;
                }

                textarea {
                    font-size: 16px;
                    font-family: 'Courier';
                    color: black;
                    width: ${this.width - 100 || '50'}px;
                    font-weight: 600;
                    flex: 1;
                    padding: 5px;
                    border:  none;
                    border-radius: 3px;
                    outline: none;
                    background-color: #FFF6D4;
                    resize: none;
                    overflow: auto; 
                }

                textarea:hover{
                    background-color: #EFE6C4;
                }
                
                textarea:focus{
                    background-color: #EFE6C4;
                }

                button {
                    font-family: 'Courier';
                    font-size: 16px;
                    padding: 5px 10px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    background-color: #595959;
                    color: #FFFCE6;
                    margin-left: 5px;
                }

                button:hover {
                    background-color: #4a4a4a;
                }
                
                button:active{
                    background-color: #333333;
                }
            </style>
            <div>
                <textarea id="text-field" type="search" placeholder="${this.placeholder || 'Search...'}"></textarea>
                <button id="textFieldButton">Send</button>
            </div>
        `;
    }
}

customElements.define("text-field", TextField);


