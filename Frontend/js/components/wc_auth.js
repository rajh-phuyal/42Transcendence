import $auth from '../auth/authentication.js';
import $nav from '../abstracts/navigationInit.js';
import $store from '../store/store.js';
import $syncer from '../sync/Syncer.js';
import router from '../navigation/router.js';
import { $id } from '../abstracts/dollars.js';
import { translate } from '../locale/locale.js';
import $callToast from '../abstracts/callToast.js';

// TODO put the css styling in a css file (for all web components)

const eventListenersConfig = [
	{
		id: "login-button",
		event: "click",
		callback: "loginButtonClick",
	},
	{
		id: "register-button",
		event: "click",
		callback: "registerButtonClick"
	},
	{
		class: ".submit-button",
		event: "click",
		callback: "submitClick"
	},
	{
		class: ".back-to-main-button",
		event: "click",
		callback: "backButtonClick"
	},
	{
		class: ".show-password-button",
		event: "click",
		callback: "togglePasswordVisibility"
	},
	{
		class: ".usernameInput",
		event: "keypress",
		callback: "handleKeyPress"
	},
	{
		class: ".passwordInput",
		event: "keypress",
		callback: "handleKeyPress",
		keyUp: "passwordMathcCheck"
	}
];

class AuthCard extends HTMLElement {

    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: "open" });
		this.displayMode = "home";
        this.usernamePlaceholder = translate("auth", "usernamePlaceholder")
        this.passwordPlaceholder = translate("auth", "passwordPlaceholder")
        this.passwordConfirmationPlaceholder = translate("auth", "passwordConfirmationPlaceholder")
		this.loginButton = translate("auth", "loginButton");
		this.registerButton = translate("auth", "registerButton")
		this.submitButton = translate("auth", "submitButton");
		this.backButton = translate("auth", "backButton");
		this.passwordVisibilityButton = translate("auth", "displayPassword");
		this.transitionTime = 300;
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

		for (let config of eventListenersConfig) {
			if (config.id) {
				const element = this.shadow.getElementById(config.id);
				element.addEventListener(config.event, this[config.callback].bind(this));
			} else {
				const elements = this.shadow.querySelectorAll(config.class);
				elements.forEach((element) => {
					element.addEventListener(config.event, this[config.callback].bind(this));
					if (config.keyUp)
						element.addEventListener("keyup", this[config.keyUp].bind(this));
				});
			}
		}
		document.addEventListener('keydown', this.handleEscapePress.bind(this));
    }

	disconnectedCallback() {
        document.removeEventListener('keydown', this.handleEscapePress);
    }

    handleEscapePress(event) {
        if (event.key === "Escape" && this.displayMode !== "home") {
            this.backButtonClick();
        }
    }

	loginErrorMessages(username, password) {
		let error = false;
		if (username.value === "" || username.value === null) {
			username.style.border = "2px solid red";
			error = true;
		}
		if (password.value === "" || password.value === null) {
			password.style.border = "2px solid red";
			error = true;
		}
		return (error);
	}

	regiterErrorMessages(username, password, passwordConfirmation) {
		let errorMsg = "";
		const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])(?=.*\W)(?!.* ).{8,}$/;
		switch (true) {
			case username.value === "" || username.value === null:
				username.style.border = "2px solid red";
			case password.value === "" || password.value === null:
				password.style.border = "2px solid red";
			case passwordConfirmation.value === "" || passwordConfirmation.value === null:
				passwordConfirmation.style.border = "2px solid red";
				break ;
			case password.value != passwordConfirmation.value:
				password.style.border = "2px solid red";
				passwordConfirmation.style.border = "2px solid red";
				if (errorMsg.length != 0)
					errorMsg += " and "; // TODO Translate
				errorMsg += "passwords do not match"; // TODO Translate
				break ;
			case !passwordRegex.test(password.value):
				password.style.border = "2px solid red";
				passwordConfirmation.style.border = "2px solid red";
				if (errorMsg.length != 0)
					errorMsg += " and "; // TODO Translate
				errorMsg += "password must contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one number and one special character"; // TODO Translate
			default:
				break ;
		}
		if (errorMsg.length != 0)
			$callToast("error", errorMsg);
		return (errorMsg.length != 0);
	}

    submitClick() {
		let usernameField;
		let passwordField;

		if (this.displayMode === "login") {
			usernameField = this.shadow.getElementById("username-login-input");
			passwordField = this.shadow.getElementById("password-login-input");
			if (this.loginErrorMessages(usernameField, passwordField))
					return ;
		} else if (this.displayMode === "register") {
			usernameField = this.shadow.getElementById("username-register-input");
			passwordField = this.shadow.querySelectorAll(".password-register");
			if (this.regiterErrorMessages(usernameField, passwordField[0], passwordField[1]))
				return ;
			passwordField = passwordField[0];
		}

        // todo: block if empty and other validations

        // usernameField.blur();
        // passwordField.blur();

        const authAction = this.displayMode === "login" ? "authenticate" : "createUser";
        $auth?.[authAction](usernameField?.value, passwordField?.value)
        .then((response) => {
            // Initialize the store
            $store.initializer();

            // Clear the auth cache from before the authentication
            $auth.clearAuthCache();

            // Set this directly to avoid race condition
            $auth.isAuthenticated = true;

            // Update the store with the new user data
            $store.commit('setIsAuthenticated', true);
            $store.commit('setUser', {
                id: response.userId,
                username: response.username
            });

            // reinitializes the nav bar
            $nav();

            const successToast = $id('logged-in-toast');
            new bootstrap.Toast(successToast, { autohide: true, delay: 5000 }).show();

            this.showNav();

			// broadcast login to other tabs
			$syncer.broadcast("authentication-state", { login: true });

            // Add small delay to ensure store updates are processed
            router("/home");
        })
        .catch(error => {
			$callToast("error", error.message);
            // console.error(error);
        })
        .finally(() => {
            // usernameField.value = "";
            // passwordField.value = "";
        });
    }

    handleKeyPress(event) {
		if (event.key === 'Enter')
			this.submitClick();
		if (event.target.classList.contains("usernameInput"))
			event.target.style.border = "3px solid #FFF6D4";
    }

	delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

	async loginButtonClick() {
		const loginButton = this.shadow.getElementById("login-button");
		const registerButton = this.shadow.getElementById("register-button");
		const loginSection = this.shadow.getElementById("login-section");

		loginButton.classList.add("fade");
		registerButton.classList.add("fade");

		await this.delay(this.transitionTime);

		loginButton.style.display = "none";
		registerButton.style.display = "none";
		loginSection.style.display = "flex";

		await this.delay(this.transitionTime);
		loginSection.classList.remove("fade");
		this.displayMode = "login";
	}

	async registerButtonClick() {
		console.log("registerButtonClick");
		const loginButton = this.shadow.getElementById("login-button");
		const registerButton = this.shadow.getElementById("register-button");
		const registerSection = this.shadow.getElementById("register-section");

		loginButton.classList.add("fade");
		registerButton.classList.add("fade");

		await this.delay(this.transitionTime);
		loginButton.style.display = "none";
		registerButton.style.display = "none";
		registerSection.style.display = "flex";

		await this.delay(this.transitionTime);
		registerSection.classList.remove("fade");
		this.displayMode = "register";
	}


	async backButtonClick() {
		const loginButton = this.shadow.getElementById("login-button");
		const registerButton = this.shadow.getElementById("register-button");
		const loginSection = this.shadow.getElementById("login-section");
		const registerSection = this.shadow.getElementById("register-section");

		loginSection.classList.add("fade");
		registerSection.classList.add("fade");

		await this.delay(this.transitionTime);

		loginSection.style.display = "none";
		registerSection.style.display = "none";
		loginButton.style.display = "block";
		registerButton.style.display = "block";

		await this.delay(this.transitionTime);
		loginButton.classList.remove("fade");
		registerButton.classList.remove("fade");
		this.displayMode = "home";
	}

	togglePasswordVisibility(event) {
		event.target.previousElementSibling.type = event.target.previousElementSibling.type === "password" ? "text" : "password";
		event.target.textContent = event.target.textContent === translate('auth', 'displayPassword') ?
			translate("auth", "hidePassword") : translate("auth", "displayPassword");
	}

	passwordMathcCheck() {
		const passwordField = this.shadow.querySelectorAll(".password-register");
		if (passwordField[0].value === passwordField[1].value) {
			passwordField[0].style.border = "3px solid #FFF6D4";
			passwordField[1].style.border = "3px solid #FFF6D4";
			console.log("passwords match");
		} else {
			passwordField[0].style.border = "3px solid red";
			passwordField[1].style.border = "3px solid red";
			console.log("passwords do not match");
		}
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

			.show-password-button {
				position: absolute;
				right: calc(10% - 1.5rem);
				top: calc(50% - 1.5rem);
				width: auto;
				height: 3rem;
				font-size: 1.5rem;
				font-family: 'Courier';
				font-weight: 700;
				cursor: pointer;
				border: 1px solid #FFF6D4;
				background-color: #100C09;
				border-radius: 0.2rem;
				color: #FFF6D4;
			}

			#password-register-visibility-toogle-button {
				right: calc(10% - 1.5rem);
				top: calc(40% - 2rem);
			}

			#password-confirmation-visibility-toogle-button {
				right: calc(10% - 1.5rem);
				top: calc(54% - 1rem);
			}
            </style>

            <div class="main-container">

				<button id="login-button">${this.loginButton}</button>
				<button id="register-button">${this.registerButton}</button>

				<section id="login-section" style="display:none;" class="fade">
					<input id="username-login-input" class="usernameInput" placeholder="${this.usernamePlaceholder}"/>
					<input id="password-login-input" class="passwordInput" placeholder="${this.passwordPlaceholder}" type="Password">
					<button class="show-password-button">${this.passwordVisibilityButton}</button>
					<div class="buttons-container">
						<button id="submit-login" class="submit-button">${this.submitButton}</button>
						<button class="back-to-main-button">${this.backButton}</button>
					</div>
				</section>

				<section id="register-section" style="display:none;" class="fade">
					<input id="username-register-input" class="usernameInput" placeholder="${this.usernamePlaceholder}"/>
					<input id="password-register-input" class="passwordInput password-register" placeholder="${this.passwordPlaceholder}" type="Password">
					<button id="password-register-visibility-toogle-button" class="show-password-button">${this.passwordVisibilityButton}</button>
					<input class="password-confirmation-input passwordInput password-register" placeholder="${this.passwordConfirmationPlaceholder}" type="Password">
					<button id="password-confirmation-visibility-toogle-button" class="show-password-button">${this.passwordVisibilityButton}</button>
					<div class="buttons-container">
						<button id="submit-register" class="submit-button">${this.submitButton}</button>
						<button class="back-to-main-button">${this.backButton}</button>
					</div>
				</section>

			</div>
			`;
		}
	}

customElements.define("auth-card", AuthCard);
