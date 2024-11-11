import $auth from '../auth/authentication.js';
import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id } from '../abstracts/dollars.js';
// TODO put the css styling in a css file (for all web components)


class AuthCard extends HTMLElement {
	
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
    }

    static get observedAttributes() {
        return ["login"];
    }

    hideNav(){
        let nav = document.getElementById('navigator');
        nav.style.display = 'none';
    }

    showNav(){
        let nav = document.getElementById('navigator');
        nav.style.display = 'flex';
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
        const usernameField = this.shadow.getElementById("usernameInput");
        const passwordField = this.shadow.getElementById("passwordInput");

        // todo: block if empty and other validations

        usernameField.blur();
        passwordField.blur();

        const authAction = this.login ? "authenticate" : "createUser";
        $auth?.[authAction](usernameField?.value, passwordField?.value)
        .then((response) => {
            console.log("auth response:", response);

            $store.commit('setIsAuthenticated', true);
            $store.commit('setJWTTokens', {
                access: response.access,
                refresh: response.refresh
            });
            $store.commit('setUser', {
                id: response.userId,
                username: response.username
            });

            const successToast = $id('logged-in-toast');
            new bootstrap.Toast(successToast, { autohide: true, delay: 5000 }).show();

            this.showNav();
            router("/home");
        })
        .catch(error => {
            console.error(error);
        })
        .finally(() => {
            usernameField.value = "";
            passwordField.value = "";
        });
    }

    secondaryButtonclick(){
        let temp = this.primaryButton;
        this.primaryButton = this.secundaryButton;
        this.secundaryButton = temp;
        this.login = !this.login;
        this.connectedCallback();
    }

    handleKeyPress(event){

        if (event.key !== 'Enter')
            return ;
        this.primaryButtonclick();
    }
    attributeChangedCallback(name, oldValue, newValue) {
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
                height: 400px;
                width: 65%;
				display: flex;
				gap: 0.5rem;
				justify-content: center;
				align-items: center;
            }

			#login-button, #register-button {
				width: 45%;
				height: 50%;
				font-size: 1.5rem;
				font-family: 'Courier';
				font-weight: 700;
				border-radius: 0.2rem;
				cursor: pointer;
				transition: background-color 0.8s ease-out, opacity 1s ease-in-out;
			}

			#login-button {
				border: 8px double #100C09;
                color: #3D3D3D;
                background-color: #FFFCE6;
			}

			#login-button:hover {
				background-color: #dbd8c1;
			}

			#login-button.fade, #register-button.fade {
				opacity: 0;
			}

			#register-button {
				color: #FFF6D4;
				background-color: #100C09;
				border: 3px solid #FFF6D4;
			}

			#register-button:hover {
				background-color: #201C19;
			}

			#login-section, #register-section {
				width: 90%;
				display: flex;
				flex-direction: column;
				justify-content: space-between;
				align-items: center;
				height: 300px;
				transition: opacity 1s ease-in-out;
			}

			#login-section.fade, #register-section.fade {
				opacity: 0;
			}

			#register-section > input {
				height: 3.5rem;
			}

			.usernameInput, .passwordInput, .password-confirmation-input {
				width: 100%;
				height: 5rem;
				font-size: 1.5rem;
                font-family: 'Courier';
				font-weight: 700;
				border-radius: 0.2rem;
				color: #FFF6D4;
				border: 3px solid #FFF6D4;
				background-color: #100C09;
			}

			.buttons-container {
				display: flex;
				gap: 0.5rem;
				justify-content: center;
				align-items: center;
				width: 100%;
			}

			.submit-button, .back-to-main-button {
				width: 50%;
				padding: 2rem;
				font-size: 1rem;
				font-family: 'Courier';
				font-weight: 700;
				border-radius: 0.2rem;
				cursor: pointer;
			}

			.submit-button {
				background-color: #FFFCE6;
			}

			.back-to-main-button {
				border: 2px solid #FFFCE6;
                color: #FFFCE6;
                background-color: #100C09;
				transition: background-color 0.8s ease-out;
			}

			.back-to-main-buton:hover {
				background-color: red;
			}
            </style>

            <div class="main-container">
				<button id="login-button">LOGIN</button>
				<button id="register-button">REGISTER</button>
				<section id="login-section" style="display:none;" class="fade">
					<input id="username-login-input" class="usernameInput" placeholder="username" required/>
					<input id="password-login-input" class="passwordInput" placeholder="password" type="Password" requiredj>
					<div class="buttons-container">
						<button id="submit-login" class="submit-button">Submit</button>
						<button class="back-to-main-button">Back</button>
					</div>
				</section>
				<section id="register-section" style="display:none;" class="fade">
					<input id="username-register-input" class="usernameInput" placeholder="username"/>
					<input id="password-register-input" class="passwordInput password-register" placeholder="password" type="Password">
					<input class="password-confirmation-input passwordInput password-register" placeholder="confirm password" type="Password">
					<div class="buttons-container">
						<button id="submit-register" class="submit-button">Submit</button>
						<button class="back-to-main-button">Back</button>
					</div>
				</section>
			</div>
			`;
		}
	}

customElements.define("auth-card", AuthCard);
