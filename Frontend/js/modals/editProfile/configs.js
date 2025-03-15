import $callToast from '../../abstracts/callToast.js';
import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import $store from '../../store/store.js';
import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {

    },

    methods: {

        initTypeListeners(init) {
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const languageElement   = this.domManip.$id("modal-edit-profile-language");
            if (init) {
                this.domManip.$on(usernameElement, "input", this.typeCallback);
                this.domManip.$on(firstNameElement, "input", this.typeCallback);
                this.domManip.$on(lastNameElement, "input", this.typeCallback);
                this.domManip.$on(languageElement, "input", this.typeCallback);
            } else {
                this.domManip.$off(usernameElement, "input", this.typeCallback);
                this.domManip.$off(firstNameElement, "input", this.typeCallback);
                this.domManip.$off(lastNameElement, "input", this.typeCallback);
                this.domManip.$off(languageElement, "input", this.typeCallback);
            }
        },

        typeCallback(event) {
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const languageElement   = this.domManip.$id("modal-edit-profile-language");
            const submitButton      = this.domManip.$id("modal-edit-profile-btn-save");
            if (usernameElement.value.trim() !== "" && firstNameElement.value.trim() !== "" && lastNameElement.value.trim() !== "" && languageElement.value.trim() !== "")
                submitButton.disabled = false;
            else
                submitButton.disabled = true;
        },

        submitCallback() {
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const languageElement   = this.domManip.$id("modal-edit-profile-language");

            call("user/update-user-info/", "PUT", {
                username: usernameElement.value.trim(),
                firstName: firstNameElement.value.trim(),
                lastName: lastNameElement.value.trim(),
                language: languageElement.value.trim(),
            }).then(data => {
                console.warn(data);
                if (!data.status === "success")
                    return;
                $callToast("success", data.message);
                this.$store.commit("setLocale", language);
                router('/profile', { id: $store.fromState("user").id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },
    },

    hooks: {
        beforeOpen() {
            const avatarElement     = this.domManip.$id("modal-edit-profile-avatar");
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const languageElement   = this.domManip.$id("modal-edit-profile-language");
            const submitElement     = this.domManip.$id("modal-edit-profile-btn-save");
            // Placeholders
            usernameElement.placeholder = "username"; // TODO: translate
            firstNameElement.placeholder = "first name"; // TODO: translate
            lastNameElement.placeholder = "last name"; // TODO: translate
            // Values
            usernameElement.value = this.domManip.$id("router-view").getAttribute("data-user-username");
            firstNameElement.value = this.domManip.$id("router-view").getAttribute("data-user-first-name");
            lastNameElement.value = this.domManip.$id("router-view").getAttribute("data-user-last-name");
            languageElement.value = this.domManip.$id("router-view").getAttribute("data-user-language");
            // Avatar
            avatarElement.src = window.origin + '/media/avatars/' + this.domManip.$id("router-view").getAttribute("data-user-avatar");
            // Add Event Listeners
            this.initTypeListeners(true);
            this.domManip.$on(submitElement, "click", this.submitCallback);
            return true;
        },
        afterClose () {
            // Remove Event Listeners
            const submitElement     = this.domManip.$id("modal-edit-profile-btn-save");
            this.initTypeListeners(false);
            this.domManip.$off(submitElement, "click", this.submitCallback);
        }
    }
}