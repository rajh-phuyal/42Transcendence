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
            .main-container {
				position: absolute;
				top: 50%;
				left: 50%;
				transform: translate(-50%, -31.5%);
				z-index: 1;
                display: flex;
                flex-direction: column;
                height: 46%;
                width: 65%;
				gap: 0.8rem;
				align-items: center;
				justify-content: space-around;
            }

			.main-container > input {
				position: relative;
				width: 90%;
				height: 2rem;
				font-size: 1.5rem;
                font-family: 'Courier';
                color: #FFF6D4;
				padding: 1.2rem 0;
                border: 3px solid #FFF6D4;
                border-radius: 0.2rem;
                background-color: #100C09;
                resize: none;
                overflow: auto;
				text-align: center;
			}

            .buttons-container{
                display: flex;
                flex-direction: row;
				justify-content: space-around;
                width: 100%;
            }

            input:hover{
                background-color: #201C19;
            }

            input:focus{
                background-color: #201C19;
            }
            
            .buttons-container > button {
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: 'Courier';
                font-size: 35px;
                font-weight: 700;
                padding: 0.5rem;
                border-radius: 0.2rem;
                cursor: pointer;
                width: 40%;
                height: 100%;
                border: 8px double #100C09;
                color: #3D3D3D;
                background-color: #FFFCE6; 
            }

            .buttons-container > .secundary-button{
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
				<input id="usernameInput" placeholder="username"/>
				<input id="passwordInput" placeholder="password" type="Password">
				<div class="buttons-container">
					<button id="primaryButton">${this.primaryButton}</button>
					<button class="secundary-button" id="secundaryButton">${this.secundaryButton}</button>
				</div>
			</div>
				`;
		}
	}

customElements.define("auth-card", AuthCard);
