// TODO put the css styling in a css file (for all web components)

import call from "../abstracts/call.js";

class AuthCard extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes() {
        return ["login"];
    }

    hideNav(){
        var nav = document.getElementById('navigator');
        nav.style.display = 'none';
    }

    connectedCallback() {
        this.render();
        const primaryButtonElement = this.shadow.getElementById("primaryButton");
        primaryButtonElement.addEventListener('click', this.primaryButtonclick.bind(this));
        const secondaryButtonElement = this.shadow.getElementById("secundaryButton");
        secondaryButtonElement.addEventListener('click', this.secondaryButtonclick.bind(this));
        const inputElement1 = this.shadow.getElementById("usernameInput");
        inputElement1.addEventListener('keypress', this.handleKeyPress.bind(this));
        const inputElement2 = this.shadow.getElementById("passwordInput");
        inputElement2.addEventListener('keypress', this.handleKeyPress.bind(this));
    }

    primaryButtonclick(){
        const inputElement1 = this.shadow.getElementById("usernameInput");
        const inputElement2 = this.shadow.getElementById("passwordInput");

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

    secondaryButtonclick(){
            
        let temp = this.primaryButton;
        this.primaryButton = this.secundaryButton;
        this.secundaryButton = temp;
        this.login = !this.login;
        console.log(this.login);
        this.connectedCallback();
    }

    handleKeyPress(event){

        if (event.key !== 'Enter')
            return ;
        this.primaryButtonclick();
    }
    attributeChangedCallback(name, oldValue, newValue) {
        console.log(name, ":", newValue);
        if (name === "login") {
            if (newValue === "true" || newValue === "True")
            {
                this.login = true;
                this.primaryButton = "LOGIN";
                this.secundaryButton = "REGISTER";
            }
            else
            {
                this.login = false;
                this.primaryButton = "REGISTER";
                this.secundaryButton = "LOGIN";
            }
        }
        this.render();
    }

    render() {
        this.hideNav();
        this.shadow.innerHTML = `
            <style>
            .main-container{
                display: flex;
                flex-direction: column;
                height: 410px;
                width: 585px
            }

            .buttons-container{
                display: flex;
                flex-direction: row;
                margin: 30px 0px;
                width: 585px;
            }

            input {
                font-size: 25px;
                font-family: 'Courier';
                color: #FFF6D4;
                width: 500px;
                height: 35px;
                flex: 1;
                padding: 5px;
                margin: 30px;
                border:  3px solid #FFF6D4;
                border-radius: 3px;
                background-color: #100C09;
                resize: none;
                overflow: auto; 
            }

            input:hover{
                background-color: #201C19;
            }

            input:focus{
                background-color: #201C19;
            }
            
            button {
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: 'Courier';
                font-size: 35px;
                font-weight: 700;
                margin: 0px 30px;
                padding: 3px;
                border-radius: 2px;
                cursor: pointer;
                width: 225px;
                height: 80px;
                border: 8px double #100C09;
                color: #3D3D3D;
                background-color: #FFFCE6; 
            }

            .secundary-button{
                border: 2px solid #FFFCE6;
                color: #FFFCE6;
                background-color: #100C09; 
            }

            button:hover{
                background-color: #EFECD6;
            }

            button:active{
                background-color: #DFDCC6;
            }
            
            .secundary-button:hover{
                background-color: #201C19;
            }

            .secundary-button:active{
                background-color: #302C29;
            }
            </style>

            <div class="main-container">
                <input id="usernameInput" placeholder="username"></input>
                <input id="passwordInput" placeholder="password" type="Password"></input>
                <div class="buttons-container">
                    <button id="primaryButton">${this.primaryButton}</button>
                    <button class="secundary-button" id="secundaryButton">${this.secundaryButton}</button>
                <div>
            </div>
        `;
    }
}

customElements.define("auth-card", AuthCard);


