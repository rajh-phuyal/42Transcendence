import call from '../../abstracts/call.js'
import { $id, $on, $queryAll, $off, $class } from '../../abstracts/dollars.js';
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
            const element = $id("avatar");
            element.src = 'https://localhost/media/avatars/' + this.result.avatarUrl;
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
            let element = $id("button-top-left");
            if (this.buttonTopLeft.image)
                element.src = this.buttonTopLeft.image;
            else
                element.style.display = "none";
            element = $id("button-top-middle");
            element.src = this.buttonTopMiddle.image;
            element = $id("button-top-right");
            if (this.buttonTopRight.image)
                element.src = this.buttonTopRight.image;
            else
                element.style.display = "none";
            element = $id("button-bottom-left");
            element.src = "../../../../assets/profileView/gamingHistoryIcon.png";
            element = $id("button-bottom-right");
            element.src = "../../../../assets/profileView/FriendsListIcon.png";
        },
        
        populateButtons(){
            this.setupTopLeftButton();
            this.setupTopMiddleButton();
            this.setupTopRightButton();
            this.putImagesInButtons();
        },

        blackout() {

            let elements = $queryAll(".blackout, .game-stats-parameters, .progress, .last-seen-image, .button-bottom-left, .button-bottom-right")
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }
        },

        hideElement(elementId){
            let element = $id(elementId)
            element.style.display = "none";
        },

        hideModal(modalToHide) {
            let modalElement = $id(modalToHide);
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
        },

        showElement(elementId){
            let element = $id(elementId)
            element.style.display = "block";
        },

        profileEditMethod() {
            this.hideElement("edit-profile-modal-avatar-change");   
            this.hideElement("edit-profile-modal-password-change");
            this.showElement("edit-profile-modal-form");

            $id("edit-profile-modal-form-input-first-name").value = this.result.firstName;
            $id("edit-profile-modal-form-input-last-name").value = this.result.lastName;
            $id("edit-profile-modal-form-input-username").value = this.result.username;
            $id("edit-profile-modal-form-language-selector").value = $store.fromState("locale");
            

            let modalElement = $id("edit-profile-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        changePasswordMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-password-change");
            $id("edit-profile-modal").focus();
        },

        changeAvatarMethod() {
            this.hideElement("edit-profile-modal-form");
            this.showElement("edit-profile-modal-avatar-change");
            this.hideElement("edit-profile-modal-avatar-change-crop-image");
            $id("edit-profile-modal").focus();
        },

        friendshipMethod() {

            let blockIndex;
            if (this.result.relationship.isBlocking)
                blockIndex = "blocked";
            else
                blockIndex = "unblocked";

            // friendship portion of the modal
            let element = $id("friendshp-modal-friendship-text")
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
                element = $id("friendshp-modal-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }

            let modalElement = $id("friendship-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        openFileExplorer() {
            let element = $id("edit-profile-modal-avatar-change-file-input");
            element.click();
        },

        callFormData(blob) {
            const formData = new FormData();
            formData.append('avatar', blob, 'avatar.png');
            
            fetch('https://localhost/api/user/update-avatar/', {
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
                    let uploadedImage = $id("edit-profile-modal-avatar-change-uploaded-image");
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
            const oldPassword = $id("edit-profile-modal-password-change-input-old-password").value;
            const newPassword = $id("edit-profile-modal-password-change-input-new-password").value;
            const repeatPassword = $id("edit-profile-modal-password-change-input-repeat-password").value;
            
            console.log("new password:", oldPassword);
            console.log("new password:", newPassword);
            console.log("rep password:", repeatPassword);

            if (newPassword !== repeatPassword)
                console.log("Error: Passwords dont match");
            else
                console.log("Success! Password changed!!");
        },

        submitForm() {
            

            const firstName = $id("edit-profile-modal-form-input-first-name").value;
            const lastName = $id("edit-profile-modal-form-input-last-name").value;
            const username = $id("edit-profile-modal-form-input-username").value;
            const language = $id("edit-profile-modal-form-language-selector").value;

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

            $id("invite-for-game-modal-opponent-photo").src = 'https://localhost/media/avatars/' + this.result.avatarUrl;
            console.log("username:", this.result.username);
            $id("invite-for-game-modal-opponent-name").textContent = this.result.username;

            console.log("yooo");
            let modalElement = $id("invite-for-game-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
        },
        selectMap(chosenMap) {
            const maps = $class("invite-for-game-modal-maps-button");
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
    },


    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            let element = $id("button-top-left");
            $off(element, "click", this.buttonTopLeft.method);
            element = $id("button-top-middle");
            $off(element, "click", this.buttonTopMiddle.method);
            element = $id("button-top-right");
            $off(element, "click", this.buttonTopRight.method);
            element = $id("edit-profile-modal-form-change-password-button");
            $off(element, "click", this.changePasswordMethod);
            element = $id("edit-profile-modal-form-change-avatar-button");
            $off(element, "click", this.changeAvatarMethod);
            element = $id("edit-profile-modal-avatar-change-upload-button");
            $off(element, "click", this.openFileExplorer);
            element = $id("edit-profile-modal-avatar-change-file-input");
            $off(element, "change", this.extractFile);
            element = $id("edit-profile-modal-avatar-change-crop-image");
            $off(element, "click", this.submitAvatar);
            element = $id("edit-profile-modal-form-submit-button");
            $off(element, "click", this.submitForm);
            element = $id("edit-profile-modal-password-change-submit-button");
            $off(element, "click", this.submitNewPassword);
            element = $id("friendship-modal-friendship-primary-button");
            $off(element, "click", this.changeFrendshipPrimaryMethod);
            element = $class("invite-for-game-modal-maps-button");
            for (let HTMLelement of element)
                $off(HTMLelement, "click", this.selectMap);
            element = $id("invite-for-game-modal-powerups-checkbox");
            $off(element, "change", () => {this.gameSettings.powerups = !this.gameSettings.powerups;});
            element = $id("invite-for-game-modal-start-button");
            $on(element, "click", this.submitInvitation);
            element = $id("friendship-modal-friendship-secondary-button");
            $off(element, "click", this.changeFrendshipSecondaryMethod);
            element = $id("friendship-modal-block-button");
            $off(element, "click", this.changeBlockMethod);
            element = $id("friendship-modal-cancel-button");
            $on(element, "click", this.cancelButton);

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
                    let element = $id("button-top-left");
                    $on(element, "click", this.buttonTopLeft.method);
                }
                if (this.buttonTopMiddle.method) {
                    let element = $id("button-top-middle");
                    $on(element, "click", this.buttonTopMiddle.method);
                }
                if (this.buttonTopRight.method) {
                    let element = $id("button-top-right");
                    $on(element, "click", this.buttonTopRight.method);
                }

                this.openInviteForGameModal(); // Just for building the modal

                let element = $id("edit-profile-modal-form-change-password-button");
                $on(element, "click", this.changePasswordMethod);
                element = $id("edit-profile-modal-form-change-avatar-button");
                $on(element, "click", this.changeAvatarMethod);
                element = $id("edit-profile-modal-avatar-change-upload-button");
                $on(element, "click", this.openFileExplorer);
                element = $id("edit-profile-modal-avatar-change-file-input");
                $on(element, "change", this.extractFile);
                element = $id("edit-profile-modal-avatar-change-crop-image");
                $on(element, "click", this.submitAvatar);
                element = $id("edit-profile-modal-form-submit-button");
                $on(element, "click", this.submitForm);
                element = $id("edit-profile-modal-password-change-submit-button");
                $on(element, "click", this.submitNewPassword);
                element = $id("friendship-modal-friendship-primary-button");
                $on(element, "click", this.changeFrendshipPrimaryMethod);
                element = $class("invite-for-game-modal-maps-button");
                for (let HTMLelement of element)
                    $on(HTMLelement, "click", this.selectMap);
                element = $id("invite-for-game-modal-powerups-checkbox");
                $on(element, "change", () => {this.gameSettings.powerups = !this.gameSettings.powerups;});
                element = $id("invite-for-game-modal-start-button");
                $on(element, "click", this.submitInvitation);
                element = $id("friendship-modal-friendship-secondary-button");
                $on(element, "click", this.changeFrendshipSecondaryMethod);
                element = $id("friendship-modal-block-button");
                $on(element, "click", this.changeBlockMethod);
                element = $id("friendship-modal-cancel-button");
                $on(element, "click", this.cancelButton);
            })
            // on error?
        },
    }
}
