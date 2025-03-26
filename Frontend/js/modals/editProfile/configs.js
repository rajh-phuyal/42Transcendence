import $callToast from '../../abstracts/callToast.js';
import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';
import $store from '../../store/store.js';
import { translate } from '../../locale/locale.js';
import { loadTranslationsForTooltips } from '../../abstracts/nav.js';

export default {
    attributes: {

    },

    methods: {
        translateElements() {
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const notesElement      = this.domManip.$id("modal-edit-profile-notes");
            // Placeholders
            usernameElement.placeholder     = translate("editProfile", "placeholderUsername");
            firstNameElement.placeholder    = translate("editProfile", "placeholderFirstName");
            lastNameElement.placeholder     = translate("editProfile", "placeholderLastName");
            // Tooltips
            notesElement.placeholder        = translate("editProfile", "placeholderNotes");
        },

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
            const noteElement       = this.domManip.$id("modal-edit-profile-notes");

            call("user/update-user-info/", "PUT", {
                username:   usernameElement.value.trim(),
                firstName:  firstNameElement.value.trim(),
                lastName:   lastNameElement.value.trim(),
                language:   languageElement.value.trim(),
                notes:      noteElement.value.trim()
            }).then(data => {
                console.warn(data);
                if (!data.status === "success")
                    return;
                $callToast("success", data.message);
                this.$store.commit("setLocale", data.locale);
                // Translate Navbar elements
                loadTranslationsForTooltips();
                router('/profile', { id: $store.fromState("user").id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },
    },

    hooks: {
        beforeOpen() {
            this.translateElements();
            const avatarElement     = this.domManip.$id("modal-edit-profile-avatar");
            const usernameElement   = this.domManip.$id("modal-edit-profile-username");
            const firstNameElement  = this.domManip.$id("modal-edit-profile-first-name");
            const lastNameElement   = this.domManip.$id("modal-edit-profile-last-name");
            const languageElement   = this.domManip.$id("modal-edit-profile-language");
            const noteElement       = this.domManip.$id("modal-edit-profile-notes");
            const submitElement     = this.domManip.$id("modal-edit-profile-btn-save");
            // Values
            usernameElement.value   = this.domManip.$id("router-view").getAttribute("data-user-username");
            firstNameElement.value  = this.domManip.$id("router-view").getAttribute("data-user-first-name");
            lastNameElement.value   = this.domManip.$id("router-view").getAttribute("data-user-last-name");
            languageElement.value   = this.domManip.$id("router-view").getAttribute("data-user-language");
            noteElement.value       = this.domManip.$id("router-view").getAttribute("data-user-notes");
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