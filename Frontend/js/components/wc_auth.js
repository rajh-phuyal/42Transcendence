import call from "../abstracts/call.js";

class AuthCard extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
        this.login;
    }

    static get observedAttributes() {
        return ["button1", "button2", "login"];
    }

    connectedCallback() {
        this.render();
        const inputElement = this.shadow.getElementById("button1");
        inputElement.addEventListener('click', this.buttonclick.bind(this));
        const inputElement2 = this.shadow.getElementById("input1");
        inputElement2.addEventListener('keypress', this.handleKeyPress.bind(this));
        const inputElement3 = this.shadow.getElementById("input2");
        inputElement3.addEventListener('keypress', this.handleKeyPress.bind(this));
    }

    buttonclick(){
        const inputElement1 = this.shadow.getElementById("input1");
        const inputElement2 = this.shadow.getElementById("input2");

        const values = {username: inputElement1.value, password: inputElement2.value};

        inputElement1.value = "";
        inputElement2.value = "";
        console.log("input values:", values);
        inputElement1.blur();
        inputElement2.blur();

        call("/home", "POST", values).then(() => {
            console.log("it came here");
        }).catch(() => {
            console.log("Error");
        })
    }

    handleKeyPress(event){

        if (event.key !== 'Enter' || event.shiftKey)
            return ;
        this.buttonclick();
    }
    attributeChangedCallback(name, oldValue, newValue) {
        if (name === "button1") {
            this.button1 = newValue;
        }
        else if (name === "button2") {
            this.button2 = newValue;
        }
        else if (name === "login") {
            this.login = true;
        }
        this.render();
    }

    render() {
        this.shadow.innerHTML = `
            <style>
            .container1{
                display: flex;
                flex-direction: column;
                margin: 332px 325px;
            }

            .container2{
                display: flex;
                flex-direction: row;
                margin: 30px 40px;
            }

            input {
                font-size: 16px;
                font-family: 'Courier';
                color: black;
                width: 300px;
                font-weight: 600;
                flex: 1;
                padding: 5px;
                margin: 30px;
                border:  none;
                border-radius: 3px;
                outline: none;
                background-color: #FFF6D4;
                resize: none;
                overflow: auto; 
            }
            
            button{
                display: flex;
                font-family: 'Courier';
                font-size: 25px;
                text-align: center;
                line-height: 50px;
                font-weight: 700;
                color: #FFFCE6;
                width: 150px;
                flex-direction: row;
                margin: 15px;
                padding: 3px;
                border: 2px solid  #595959;
                border-radius: 8px;
                background-color: #3D3D3D;
                cursor: pointer;
            }
            </style>

            <div class="container1">
                <input id="input1" placeholder="username"></input>
                <input id="input2" placeholder="password" type="Password"></input>
                <div class="container2">
                    <button id="button1">${this.button1}</button>
                    <button id="button2">${this.button2}</button>
                <div>
            </div>
        `;
    }
}

customElements.define("auth-card", AuthCard);


