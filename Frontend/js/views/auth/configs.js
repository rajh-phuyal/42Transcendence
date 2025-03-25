import { audioPlayer } from '../../abstracts/audio.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';
import $callToast from '../../abstracts/callToast.js';
import call from '../../abstracts/call.js';
import { initClient } from './initClient.js';
import $store from '../../store/store.js';
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        mode: "main", /* main, login, register */
        language: "en-US",
        eye1: false,
        eye2: false,
        icon_yes:        "../../../../assets/icons_128x128/icon_yes.png",
        icon_no:         "../../../../assets/icons_128x128/icon_no.png",
        icon_eye_open:   "../../../../assets/icons_128x128/icon_eye_open.png",
        icon_eye_closed: "../../../../assets/icons_128x128/icon_eye_closed.png",
        icon_logo:          "../../../../assets/icons_128x128/icon_barely_a_logo.png",
        icon_egg_timer:  "../../../../assets/icons_128x128/icon_egg_timer.png"
    },

    methods: {
        translateDynamic(){
            this.domManip.$id("auth-username").placeholder  = translate("auth", "placeholderUsername");
            this.domManip.$id("auth-pswd1").placeholder     = translate("auth", "placeholderPassword");
            this.domManip.$id("auth-pswd1").title           = translate("auth", "pswdPolicy");
            this.domManip.$id("auth-pswd2").placeholder     = translate("auth", "placeholderConfirmPassword");
        },
        updateView() {
            const btnLogin      = this.domManip.$id("auth-btn-login");
            const btnRegister   = this.domManip.$id("auth-btn-register");
            const btnBack       = this.domManip.$id("auth-btn-back");
            const btnSubmit     = this.domManip.$id("auth-btn-submit");
            const inputUsername = this.domManip.$id("auth-username");
            const inputUsernameV= this.domManip.$id("auth-username-validate");
            const inputPswd1    = this.domManip.$id("auth-pswd1");
            const inputPswd1Btn = this.domManip.$id("auth-btn-show-pswd1");
            const inputPswd2    = this.domManip.$id("auth-pswd2");
            const inputPswd2Btn = this.domManip.$id("auth-btn-show-pswd2");
            if (this.mode === "main") {
                inputUsername.disabled      = false;
                inputUsernameV.style.display= "block";
                inputUsernameV.src          = this.icon_logo;
                inputUsernameV.title        = translate("auth", "hurryUp");
                inputUsername.focus();
                inputPswd1.style.display    = "none";
                inputPswd1Btn.style.display = "none";
                inputPswd2.style.display    = "none";
                inputPswd2Btn.style.display = "none";
                btnLogin.style.display      = "block";
                btnRegister.style.display   = "block";
                btnBack.style.display       = "none";
                btnSubmit.style.display     = "none";
            } else if (this.mode === "login") {
                inputUsernameV.style.display= "block";
                inputUsername.disabled      = true;
                inputPswd1.style.display    = "block";
                inputPswd1.autocomplete     = "current-password";
                inputPswd1.focus();
                inputPswd1Btn.style.display = "block";
                inputPswd2.style.display    = "none";
                inputPswd2Btn.style.display = "none";
                btnLogin.style.display      = "none";
                btnRegister.style.display   = "none";
                btnBack.style.display       = "block";
                btnSubmit.style.display     = "block";
            } else if (this.mode === "register") {
                inputUsernameV.style.display= "block";
                inputUsername.disabled      = true;
                inputPswd1.style.display    = "block";
                inputPswd1.autocomplete     = "new-password";
                inputPswd1.focus();
                inputPswd1Btn.style.display = "block";
                inputPswd2.style.display    = "block";
                inputPswd2Btn.style.display = "block";
                btnLogin.style.display      = "none";
                btnRegister.style.display   = "none";
                btnBack.style.display       = "block";
                btnSubmit.style.display     = "block";
            }
        },
        updateFlags() {
            const flagElementUS  = this.domManip.$id("button-local-en-US");
            const flagElementPTP = this.domManip.$id("button-local-pt-PT");
            const flagElementPTB = this.domManip.$id("button-local-pt-BR");
            const flagElementDE  = this.domManip.$id("button-local-de-DE");
            const flagElementUK  = this.domManip.$id("button-local-uk-UA");
            const flagElementNE  = this.domManip.$id("button-local-ne-NP");
            // Disable all flags
            this.domManip.$removeClass( flagElementUS,  "modal-toggle-button-enabled");
            this.domManip.$removeClass( flagElementPTP, "modal-toggle-button-enabled");
            this.domManip.$removeClass( flagElementPTB, "modal-toggle-button-enabled");
            this.domManip.$removeClass( flagElementDE,  "modal-toggle-button-enabled");
            this.domManip.$removeClass( flagElementUK,  "modal-toggle-button-enabled");
            this.domManip.$removeClass( flagElementNE,  "modal-toggle-button-enabled");
            this.domManip.$addClass( flagElementUS,  "modal-toggle-button-disabled");
            this.domManip.$addClass( flagElementPTP, "modal-toggle-button-disabled");
            this.domManip.$addClass( flagElementPTB, "modal-toggle-button-disabled");
            this.domManip.$addClass( flagElementDE,  "modal-toggle-button-disabled");
            this.domManip.$addClass( flagElementUK,  "modal-toggle-button-disabled");
            this.domManip.$addClass( flagElementNE,  "modal-toggle-button-disabled");
            // Enable the selected flag
            const enabledElement = this.domManip.$id(`button-local-${this.language}`);
            this.domManip.$removeClass( enabledElement,   "modal-toggle-button-disabled");
            this.domManip.$addClass(    enabledElement,   "modal-toggle-button-enabled");
        },
        /* BUTTON CALLBACKS */
        callbackLogin(event) {
            const inputUsernameV= this.domManip.$id("auth-username-validate");
            const imageYes     = this.icon_yes;
            const imageNo      = this.icon_no;
            this.apiCallDoesUsernameExist().then(exists => {
                if (exists) {
                    inputUsernameV.src= imageYes;
                    inputUsernameV.title= translate("auth", "userNameExists");
                } else {
                    inputUsernameV.src= imageNo;
                    inputUsernameV.title= translate("auth", "userNameDoesNotExists");
                }
                this.mode = "login";
                this.updateView();
            });
        },
        callbackRegister(event) {
            const inputUsernameV= this.domManip.$id("auth-username-validate");
            const imageYes     = this.icon_yes;
            const imageNo      = this.icon_no;
            this.apiCallDoesUsernameExist().then(exists => {
                if (exists) {
                    inputUsernameV.src= imageNo;
                    inputUsernameV.title= translate("auth", "userNameIsNotAvailable");
                } else {
                    inputUsernameV.src= imageYes;
                    inputUsernameV.title= translate("auth", "userNameIsAvailable");
                }
                this.mode = "register";
                this.updateView();
            });
        },
        callbackBack(event) {
            this.mode = "main";
            this.updateView();
        },
        callbackSubmit(event) {
            const inputUsername = this.domManip.$id("auth-username");
            const inputPswd1    = this.domManip.$id("auth-pswd1");
            if (this.mode === "login") {
                // Login
                initClient(false, inputUsername.value, inputPswd1.value, this.language);
            } else if (this.mode === "register") {
                // check if passwords match
                const inputPswd1    = this.domManip.$id("auth-pswd1");
                const inputPswd2    = this.domManip.$id("auth-pswd2");
                if (inputPswd1.value !== inputPswd2.value) {
                    $callToast("error", translate("auth", "pswdMissmatch"));
                    return;
                }
                // Register
                initClient(true, inputUsername.value, inputPswd1.value, this.language);
            }
        },
        /* INPUT CALLBACKS */
        callbackUsernameInput(event) {
            const inputUsername = this.domManip.$id("auth-username");
            const btnLogin      = this.domManip.$id("auth-btn-login");
            const btnRegister   = this.domManip.$id("auth-btn-register");
            const inputUsernameV= this.domManip.$id("auth-username-validate");
            inputUsername.value = inputUsername.value.trim();
            if(!inputUsername.value || (inputUsername.value.length == 0)) {
                btnLogin.disabled = true;
                btnRegister.disabled = true;
                inputUsernameV.src = this.icon_logo;
            } else {
                btnLogin.disabled = false;
                btnRegister.disabled = false;
                inputUsernameV.src = this.icon_egg_timer;
            }
        },
        callbackUsernameKey(event) {
            // On enter click login
            if (event.key === "Enter") {
                event.preventDefault();
                const inputUsername = this.domManip.$id("auth-username");
                if(this.mode === "main" && inputUsername.value)
                    this.callbackLogin();
                else {
                    const inputPswd1    = this.domManip.$id("auth-pswd1");
                    inputPswd1.focus();
                }
            } else if (event.key === "Escape") {
                event.preventDefault();
                const inputUsername = this.domManip.$id("auth-username");
                inputUsername.value = "";
            }
        },
        /* PSWD 1 */
        callbackPswd1Input(event) {
            // Check if password is valid
            const inputPswd1    = this.domManip.$id("auth-pswd1");
            const btnSubmit     = this.domManip.$id("auth-btn-submit");
            const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])(?=.*\W)(?!.* ).{8,}$/;
            // Enable / Disable the submit button
            if (!inputPswd1.value)
                btnSubmit.disabled = true;
            else
                btnSubmit.disabled = false;
            // Make the border color
            if (!inputPswd1.value) {
                inputPswd1.classList.remove("border-green");
                inputPswd1.classList.remove("border-red");
            } else if (passwordRegex.test(inputPswd1.value) && (this.mode === "register")) {
                // Add the class border-green
                inputPswd1.classList.add("border-green");
                inputPswd1.classList.remove("border-red");
            } else if ((this.mode === "register")) {
                inputPswd1.classList.remove("border-green");
                inputPswd1.classList.add("border-red");
            }
        },
        callbackPswd1Key(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                const inputPswd1    = this.domManip.$id("auth-pswd1");
                if (this.mode === "login" && inputPswd1.value)
                    this.callbackSubmit();
                else if (this.mode === "register")
                    this.domManip.$id("auth-pswd2").focus();
            } else if (event.key === "Escape") {
                event.preventDefault();
                this.callbackBack();
            }
        },
        /* PSWD 2 */
        callbackPswd2Input(event) {
            const inputPswd1    = this.domManip.$id("auth-pswd1");
            const inputPswd2    = this.domManip.$id("auth-pswd2");
            if (!inputPswd2.value) {
                inputPswd2.classList.remove("border-green");
                inputPswd2.classList.remove("border-red");
            } else if (inputPswd1.value === inputPswd2.value) {
                // Add the class border-green
                inputPswd2.classList.add("border-green");
                inputPswd2.classList.remove("border-red");
            } else {
                inputPswd2.classList.remove("border-green");
                inputPswd2.classList.add("border-red");
            }

        },
        callbackPswd2Key(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                this.callbackSubmit();
            } else if (event.key === "Escape") {
                event.preventDefault();
                const inputPswd1    = this.domManip.$id("auth-pswd1");
                inputPswd1.focus();
            }
        },
        /* FLAG */
        flagCallback(event) {
            this.language = event.target.value;
            $store.commit('setLocale', this.language);
            // Translate all filter inputs // TODO: doesnt work!
            const filerElements = this.domManip.$class("search-box");
            for (const element of filerElements)
                element.setAttribute("placeholder", translate("global:nav", "placeholderSearchbar"));
            this.updateFlags();
            // Translate view
            router("/auth");
        },
        eyeCallback(event) {
            const field = event.target.getAttribute("value");
            if(field === "1") {
                this.eye1 = !this.eye1;
                const inputPswd1 = this.domManip.$id("auth-pswd1");
                inputPswd1.type = this.eye1 ? "text" : "password";
                // Change the image
                const imgPswd1 = this.domManip.$id("auth-btn-show-pswd1");
                imgPswd1.src = this.eye1 ? this.icon_eye_open : this.icon_eye_closed;
            } else if (field === "2") {
                this.eye2 = !this.eye2;
                const inputPswd2 = this.domManip.$id("auth-pswd2");
                inputPswd2.type = this.eye2 ? "text" : "password";
                // Change the image
                const imgPswd2 = this.domManip.$id("auth-btn-show-pswd2");
                imgPswd2.src = this.eye2 ? this.icon_eye_open : this.icon_eye_closed;
            }
            // Deactive the button for asthetics
            event.srcElement.blur();
        },
        apiCallDoesUsernameExist() {
            const inputUsername = this.domManip.$id("auth-username");
            const username = inputUsername.value.trim();
            if (!username)
                return Promise.resolve(true);
            // Use search endpoint to check if username exists
            return call(`user/usernameExists/${username}/`, "GET", null, false).then(data => {
                return data.exists;
            }).catch((error) => {
                return false;
            });
        }
    },
    hooks: {
        beforeRouteEnter() {
            audioPlayer.stop();
        },

        beforeRouteLeave() {

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            const oldLanguage = $store.fromState("locale");
            if(oldLanguage) {
                this.language = oldLanguage;
                this.updateFlags();
            }
            // Translate placeholder
            this.translateDynamic();
            // Update View
            this.updateView();
            // Add event listeners
            EventListenerManager.linkEventListener("auth-btn-login",      "auth", "click",    this.callbackLogin);
            EventListenerManager.linkEventListener("auth-btn-register",   "auth", "click",    this.callbackRegister);
            EventListenerManager.linkEventListener("auth-btn-back",       "auth", "click",    this.callbackBack);
            EventListenerManager.linkEventListener("auth-btn-submit",     "auth", "click",    this.callbackSubmit);
            EventListenerManager.linkEventListener("auth-username",       "auth", "input",    this.callbackUsernameInput);
            EventListenerManager.linkEventListener("auth-username",       "auth", "keydown",  this.callbackUsernameKey);
            EventListenerManager.linkEventListener("auth-pswd1",          "auth", "input",    this.callbackPswd1Input);
            EventListenerManager.linkEventListener("auth-pswd1",          "auth", "keydown",  this.callbackPswd1Key);
            EventListenerManager.linkEventListener("auth-pswd2",          "auth", "input",    this.callbackPswd2Input);
            EventListenerManager.linkEventListener("auth-pswd2",          "auth", "keydown",  this.callbackPswd2Key);
            /* FLAGS */
            EventListenerManager.linkEventListener("button-local-en-US",  "auth", "click", this.flagCallback);
            EventListenerManager.linkEventListener("button-local-pt-PT",  "auth", "click", this.flagCallback);
            EventListenerManager.linkEventListener("button-local-pt-BR",  "auth", "click", this.flagCallback);
            EventListenerManager.linkEventListener("button-local-de-DE",  "auth", "click", this.flagCallback);
            EventListenerManager.linkEventListener("button-local-uk-UA",  "auth", "click", this.flagCallback);
            EventListenerManager.linkEventListener("button-local-ne-NP",  "auth", "click", this.flagCallback);
            /* EYE SHOW PSWD */
            EventListenerManager.linkEventListener("auth-btn-show-pswd1",  "auth", "click", this.eyeCallback);
            EventListenerManager.linkEventListener("auth-btn-show-pswd2",  "auth", "click", this.eyeCallback);
            /* FOCUS USERNAME */
            const inputUsername = this.domManip.$id("auth-username");
            inputUsername.focus();
        },
    }
}