import call from '../../abstracts/call.js'
import { populateInfoAndStats } from './script.js';
import { buttonObjects } from "./objects.js"
import router from '../../navigation/router.js';
import Cropper from '../../libraries/cropperjs/cropper.esm.js'
import $store from '../../store/store.js';
import $auth from '../../auth/authentication.js';
import $callToast from '../../abstracts/callToast.js';

export default {
    attributes: {
        buttonTopLeft: {
            image: undefined,
            method: undefined,
        },
        buttonTopMiddle: {
            image: undefined,
            method: undefined,
        },
        buttonTopRight: {
            image: undefined,
            method: undefined,
        },

        gameSettings: {
            map: "random",
            powerups: false,
        },

        result: undefined,
        cropper: undefined,

        buttonSettings: {
            friend: {
                path: "../../../../assets/profileView/friendsIcon.png",
                index: 0,
            },
            noFriend: {
                path: "../../../../assets/profileView/firendRequestIcon.png",
                index: 1,
            },
            requestReceived: {
                path: "../../../../assets/profileView/receivedFriendRequest.png",
                index: 2,
            },
            requestSent: {
                path: "../../../../assets/profileView/sentFriendRequest.png",
                index: 3,
            },
            
        }
    },

    methods: {
        insertAvatar() {
            const element = this.domManip.$id("avatar");
            element.src = window.origin + '/media/avatars/' + this.result.avatarUrl;
        },

        setupTopLeftButton() {
            if (this.result.relationship.state != "yourself")
                {
                    this.buttonTopLeft.method = this.friendshipMethod;
                    this.buttonTopLeft.image = this.buttonSettings[this.result.relationship.state].path;
                    if (this.result.relationship.isBlocking) {
                        this.buttonTopLeft.image = "../../../../assets/profileView/blockedUserIcon.png";
                    }
                }
        },
        setupTopMiddleButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopMiddle.method = this.profileEditMethod;
                this.buttonTopMiddle.image = "../../../../assets/profileView/penIcon.png";
            }
            else {
                if (this.result.newMessage)
                    this.buttonTopMiddle.image = "../../../../assets/profileView/unreadMessageIcon.png";
                else
                    this.buttonTopMiddle.image = "../../../../assets/profileView/sendMessageIcon.png";
                    this.buttonTopMiddle.method = this.messageMethod;
            }
        },
        setupTopRightButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/profileView/logoutIcon.png";
                this.buttonTopRight.method = this.logoutMethod;
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/profileView/invitePongIcon.png";
                this.buttonTopRight.method = this.openInviteForGameModal;
            }
        },
        putImagesInButtons() {
            let element = this.domManip.$id("button-top-left");
            if (this.buttonTopLeft.image)
                element.src = this.buttonTopLeft.image;
            else
                element.style.display = "none";
            element = this.domManip.$id("button-top-middle");
            element.src = this.buttonTopMiddle.image;
            element = this.domManip.$id("button-top-right");
            if (this.buttonTopRight.image)
                element.src = this.buttonTopRight.image;
            else
                element.style.display = "none";
            element = this.domManip.$id("button-bottom-left");
            element.src = "../../../../assets/profileView/gamingHistoryIcon.png";
            element = this.domManip.$id("button-bottom-right");
            element.src = "../../../../assets/profileView/FriendsListIcon.png";
        },
        
        populateButtons(){
            this.setupTopLeftButton();
            this.setupTopMiddleButton();
            this.setupTopRightButton();
            this.putImagesInButtons();
        },

        blackout() {

            let elements = this.domManip.$queryAll(".blackout, .game-stats-parameters, .progress, .last-seen-image, .button-bottom-left, .button-bottom-right")
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }
        },

        hideElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "none";
        },

        hideModal(modalToHide) {
            let modalElement = this.domManip.$id(modalToHide);
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
        },

        showElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "block";
        },

        profileEditMethod() {
            this.hideElement("edit-profile-modal-avatar-change");   
            this.hideElement("edit-profile-modal-password-change");
            this.showElement("edit-profile-modal-form");

            this.domManip.$id("edit-profile-modal-form-input-first-name").value = this.result.firstName;
            this.domManip.$id("edit-profile-modal-form-input-last-name").value = this.result.lastName;
            this.domManip.$id("edit-profile-modal-form-input-username").value = this.result.username;
            this.domManip.$id("edit-profile-modal-form-language-selector").value = $store.fromState("locale");
            

            let modalElement = this.domManip.$id("edit-profile-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        changePasswordMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-password-change");
            this.domManip.$id("edit-profile-modal").focus();
        },

        changeAvatarMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-avatar-change");
            this.hideElement("edit-profile-modal-avatar-change-crop-image");
            this.domManip.$id("edit-profile-modal").focus();
        },

        friendshipMethod() {

            let blockIndex;
            if (this.result.relationship.isBlocking)
                blockIndex = "blocked";
            else
                blockIndex = "unblocked";

            // friendship portion of the modal
            let element = this.domManip.$id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.result.relationship.state].text;
            if (this.result.relationship.state == "noFriend" && (this.result.relationship.isBlocked || this.result.relationship.isBlocking))
            {
                element.style.display = "none";
                this.hideElement("friendship-modal-friendship-primary-button");
            }

            if (!buttonObjects[this.result.relationship.state].secondaryButton)
                this.hideElement("friendship-modal-friendship-secondary-button");

            // blocking portion of the friendshop modal
            if (this.result.relationship.state == "requestReceived" || this.result.relationship.state == "requestSent")
                this.hideElement("friendship-modal-block");

            else {
                element = this.domManip.$id("friendshp-modal-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }

            let modalElement = this.domManip.$id("friendship-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
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
                headers: {
                    'Authorization': $auth.getAuthHeader(),
                }
            }).then(response => {
                if (!response.ok) {
                    console.log('Error uploading the image');
                    $callToast("error", "Error on uploading the image.")
                }
                return response.json();
            }).then(data => {
                console.log('Success:', data);
                this.hideModal("edit-profile-modal");
                $callToast("success", data.success);
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

        submitNewPassword() {
            const oldPassword = this.domManip.$id("edit-profile-modal-password-change-input-old-password").value;
            const newPassword = this.domManip.$id("edit-profile-modal-password-change-input-new-password").value;
            const repeatPassword = this.domManip.$id("edit-profile-modal-password-change-input-repeat-password").value;
            
            console.log("new password:", oldPassword);
            console.log("new password:", newPassword);
            console.log("rep password:", repeatPassword);

            if (newPassword !== repeatPassword)
                console.log("Error: Passwords dont match");
            else
                console.log("Success! Password changed!!");
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
                $callToast("success", data.success);
                router('/profile', { id: $store.fromState("user").id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        messageMethod() {
            router("/chat");
        },
        
        logoutMethod() {
            router("/logout");
        },

        changeFrendshipPrimaryMethod() {
            const object = buttonObjects[this.result.relationship.state];

            call(object.Url, object.method, { action: object.action, target_id: this.result.id }).then(data =>{
                this.hideModal("friendship-modal");
                $callToast("success", data.success);
                router('/profile', { id: this.result.id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        changeFrendshipSecondaryMethod() {
            call("user/relationship/", "DELETE", { action: "reject", target_id: this.result.id }).then(data =>{
                this.hideModal("friendship-modal");
                $callToast("success", data.success);
                router('/profile', { id: this.result.id});
            }).catch((error) => {
                console.error('Error:', error);
            });
            
        },

        changeBlockMethod() {
            let object;

            if (this.result.relationship.isBlocking)
                object = buttonObjects["blocked"];
            else
                object = buttonObjects["unblocked"];

            call(object.Url, object.method, { action: object.action, target_id: this.result.id }).then(data =>{
                this.hideModal("friendship-modal");
                $callToast("success", data.success);
                router('/profile', { id: this.result.id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        openInviteForGameModal() {

            this.domManip.$id("invite-for-game-modal-opponent-photo").src = window.origin + '/media/avatars/' + this.result.avatarUrl;
            this.domManip.$id("invite-for-game-modal-opponent-name").textContent = this.result.username;

            let modalElement = this.domManip.$id("invite-for-game-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
        },
        selectMap(chosenMap) {
            const maps = this.domManip.$class("invite-for-game-modal-maps-button");
            this.gameSettings.map = chosenMap.srcElement.name
            for (let element of maps){
                if (element.name != this.gameSettings.map)
                    element.style.opacity = 0.7;
                else
                    element.style.opacity = 1;
            }
        },
        submitInvitation() {
            console.log(this.gameSettings);
        },

        cancelButton() {
            this.hideModal("friendship-modal");
        },

        powerupsAction() {
            this.gameSettings.powerups = !this.gameSettings.powerups;
        },
    },


    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            let element = this.domManip.$id("button-top-left");
            this.domManip.$off(element, "click", this.buttonTopLeft.method);
            element = this.domManip.$id("button-top-middle");
            this.domManip.$off(element, "click", this.buttonTopMiddle.method);
            element = this.domManip.$id("button-top-right");
            this.domManip.$off(element, "click", this.buttonTopRight.method);
            element = this.domManip.$id("edit-profile-modal-form-change-password-button");
            this.domManip.$off(element, "click", this.changePasswordMethod);
            element = this.domManip.$id("edit-profile-modal-form-change-avatar-button");
            this.domManip.$off(element, "click", this.changeAvatarMethod);
            element = this.domManip.$id("edit-profile-modal-avatar-change-upload-button");
            this.domManip.$off(element, "click", this.openFileExplorer);
            element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
            this.domManip.$off(element, "change", this.extractFile);
            element = this.domManip.$id("edit-profile-modal-avatar-change-crop-image");
            this.domManip.$off(element, "click", this.submitAvatar);
            element = this.domManip.$id("edit-profile-modal-form-submit-button");
            this.domManip.$off(element, "click", this.submitForm);
            element = this.domManip.$id("edit-profile-modal-password-change-submit-button");
            this.domManip.$off(element, "click", this.submitNewPassword);
            element = this.domManip.$id("friendship-modal-friendship-primary-button");
            this.domManip.$off(element, "click", this.changeFrendshipPrimaryMethod);
            element = this.domManip.$class("invite-for-game-modal-maps-button");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            element = this.domManip.$id("invite-for-game-modal-powerups-checkbox");
            this.domManip.$off(element, "change", this.powerupsAction);
            element = this.domManip.$id("invite-for-game-modal-start-button");
            this.domManip.$off(element, "click", this.submitInvitation);
            element = this.domManip.$id("friendship-modal-friendship-secondary-button");
            this.domManip.$off(element, "click", this.changeFrendshipSecondaryMethod);
            element = this.domManip.$id("friendship-modal-block-button");
            this.domManip.$off(element, "click", this.changeBlockMethod);
            element = this.domManip.$id("friendship-modal-cancel-button");
            this.domManip.$off(element, "click", this.cancelButton);

        },

        beforeDomInsertion() {
            
        },

        afterDomInsertion() {
            console.log(this.routeParams);
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                this.result = res;
                console.log(res);
                this.insertAvatar();
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                    this.blackout();
                
                // callback functions
                if (this.buttonTopLeft.method) {
                    let element = this.domManip.$id("button-top-left");
                    this.domManip.$on(element, "click", this.buttonTopLeft.method);
                }
                if (this.buttonTopMiddle.method) {
                    let element = this.domManip.$id("button-top-middle");
                    this.domManip.$on(element, "click", this.buttonTopMiddle.method);
                }
                if (this.buttonTopRight.method) {
                    let element = this.domManip.$id("button-top-right");
                    this.domManip.$on(element, "click", this.buttonTopRight.method);
                }

                let element = this.domManip.$id("edit-profile-modal-form-change-password-button");
                this.domManip.$on(element, "click", this.changePasswordMethod);
                element = this.domManip.$id("edit-profile-modal-form-change-avatar-button");
                this.domManip.$on(element, "click", this.changeAvatarMethod);
                element = this.domManip.$id("edit-profile-modal-avatar-change-upload-button");
                this.domManip.$on(element, "click", this.openFileExplorer);
                element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
                this.domManip.$on(element, "change", this.extractFile);
                element = this.domManip.$id("edit-profile-modal-avatar-change-crop-image");
                this.domManip.$on(element, "click", this.submitAvatar);
                element = this.domManip.$id("edit-profile-modal-form-submit-button");
                this.domManip.$on(element, "click", this.submitForm);
                element = this.domManip.$id("edit-profile-modal-password-change-submit-button");
                this.domManip.$on(element, "click", this.submitNewPassword);
                element = this.domManip.$id("friendship-modal-friendship-primary-button");
                this.domManip.$on(element, "click", this.changeFrendshipPrimaryMethod);
                element = this.domManip.$class("invite-for-game-modal-maps-button");
                for (let individualElement of element)
                    this.domManip.$on(individualElement, "click", this.selectMap);
                element = this.domManip.$id("invite-for-game-modal-powerups-checkbox");
                this.domManip.$on(element, "change", this.powerupsAction);
                element = this.domManip.$id("invite-for-game-modal-start-button");
                this.domManip.$on(element, "click", this.submitInvitation);
                element = this.domManip.$id("friendship-modal-friendship-secondary-button");
                this.domManip.$on(element, "click", this.changeFrendshipSecondaryMethod);
                element = this.domManip.$id("friendship-modal-block-button");
                this.domManip.$on(element, "click", this.changeBlockMethod);
                element = this.domManip.$id("friendship-modal-cancel-button");
                this.domManip.$on(element, "click", this.cancelButton);
            })
            // on error?
        },
    }
}
