/*
TODO: THIS MODAL IS NOT DONE AT ALL!!!
    NEED TO:
        - copy the right structure from the template modal
        - double check all nodes/elements if needed?
        - adjust the js code
            - move it from original configs.js (profile/home) to congigs.js of modal!
            - make sure the js code has all values. the idea is that the view stores the info as attribute and the modal takes it from there
            - e.g. newConversation modal js!
*/

import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {

    },

    methods: {
        // TODO:
        //------------------------------
        // THIS CODE IS GOOD! JUST NEEDS TO BE REVIEWED AND ADJUSTED TO THE NEW MODAL
        //------------------------------
        /*

        changeAvatarMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-avatar-change");
            this.hideElement("edit-profile-modal-avatar-change-crop-image");
            this.domManip.$id("edit-profile-modal").focus();
        },



        openFileExplorer() {
            let element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
            element.click();
        },

        callFormData(blob) {
            const formData = new FormData();
            formData.append('avatar', blob, 'avatar.png');

            fetch(window.origin + '/api/user/update-avatar/', {
                method: 'PUT',
                body: formData,
                credentials: 'include',
            }).then(response => {
                if (!response.ok) {
                    console.log('Error uploading the image');
                    $callToast("error", "Error on uploading the image.")
                }
                return response.json();
            }).then(data => {
				$store.commit("setUser", { ...$store.fromState("user"), avatar: data.avatar_url.avatar_url });
				$id('profile-nav-avatar').src = `${window.location.origin}/media/avatars/${data.avatar_url.avatar_url}`;
                this.hideModal("edit-profile-modal");
                $callToast("success", data.message);
                router('/profile', { id: $store.fromState("user").id});
            });
        },

        submitAvatar() {

            // Extract the cropped portion of the selected image
            const croppedCanvas = this.cropper.getCroppedCanvas({
                width: 186,
                height: 208
            });

            // prepare image to send to backend
            croppedCanvas.toBlob(this.callFormData, 'image/png');
        },

        extractFile(event) {
            const file = event.target.files[0]; // Get the selected file
            if (!file || !["image/png", "image/jpeg"].includes(file.type)) {
                $callToast("error", "Invalid file type. Please select a PNG or JPEG file.");
                // TODO: close modal
                return;
            }
            if (file) {
                const reader = new FileReader(); // Create a FileReader to read the file

                reader.onload = e => {
                    let uploadedImage = this.domManip.$id("edit-profile-modal-avatar-change-uploaded-image");
                    uploadedImage.src = e.target.result; // Set the src to the image data
                    uploadedImage.style.display = 'block'; // Make the img tag visible

                    // Initialize Cropper after the image has fully loaded
                    uploadedImage.onload = () => {
                        // Destroy any previous Cropper instance before creating a new one
                        if (this.cropper) {
                            this.cropper.destroy();
                        }

                        this.cropper = new Cropper(uploadedImage, {
                            aspectRatio: 0.894, // Adjust aspect ratio as needed
                            viewMode: 1,
                        });
                        this.showElement("edit-profile-modal-avatar-change-crop-image");
                    };
                };

                reader.readAsDataURL(file); // Read the file as a data URL
            }
        },

        submitForm() {


            const firstName = this.domManip.$id("edit-profile-modal-form-input-first-name").value;
            const lastName = this.domManip.$id("edit-profile-modal-form-input-last-name").value;
            const username = this.domManip.$id("edit-profile-modal-form-input-username").value;
            const language = this.domManip.$id("edit-profile-modal-form-language-selector").value;

            call("user/update-user-info/", "PUT", {
                username: username,
                firstName: firstName,
                lastName: lastName,
                language: language
            }).then(data => {
                this.hideModal("edit-profile-modal");
                $callToast("success", data.message);
                this.$store.commit("setLocale", language);
                router('/profile', { id: $store.fromState("user").id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },


        */
    },

    hooks: {
        beforeOpen() {
            // TODO this code should come here:
//            this.hideElement("edit-profile-modal-avatar-change");
//            this.showElement("edit-profile-modal-form");
//
//            this.domManip.$id("edit-profile-modal-form-input-first-name").value = this.result.firstName;
//            this.domManip.$id("edit-profile-modal-form-input-last-name").value = this.result.lastName;
//            this.domManip.$id("edit-profile-modal-form-input-username").value = this.result.username;
//            this.domManip.$id("edit-profile-modal-form-language-selector").value = $store.fromState("locale");
//
//
//            let modalElement = this.domManip.$id("edit-profile-modal");
//            const modal = new bootstrap.Modal(modalElement);
//            modal.show();

//HERE IS FOR EDIT PROFILE MODAL
//----
//let element = this.domManip.$id("edit-profile-modal-form-change-avatar-button");
//this.domManip.$on(element, "click", this.changeAvatarMethod);
//element = this.domManip.$id("edit-profile-modal-avatar-change-upload-button");
//this.domManip.$on(element, "click", this.openFileExplorer);
//element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
//this.domManip.$on(element, "change", this.extractFile);
//element = this.domManip.$id("edit-profile-modal-avatar-change-crop-image");
//this.domManip.$on(element, "click", this.submitAvatar);
//element = this.domManip.$id("edit-profile-modal-form-submit-button");
//this.domManip.$on(element, "click", this.submitForm);
            return true;
        },
        afterClose () {
        }
    }
}