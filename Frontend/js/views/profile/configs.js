import call from '../../abstracts/call.js'
import { populateInfoAndStats } from './script.js';
import router from '../../navigation/router.js';
import Cropper from '../../libraries/cropperjs/cropper.esm.js'
import $store from '../../store/store.js';
import $auth from '../../auth/authentication.js';
import $callToast from '../../abstracts/callToast.js';
import { translate } from '../../locale/locale.js';
import { $id } from '../../abstracts/dollars.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import { modalManager } from '../../abstracts/ModalManager.js';

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

        //TODO: place this map in the store
        maps: {
            "ufo": 1,
            "lizard-people": 2,
            "snowman": 3,
            "lochness": 4,
        },

        gameSettings: {
            map: parseInt(Math.random() * (4 - 1) + 1),
            powerups: false,
        },

        result: undefined,
        cropper: undefined,

        buttonSettings: {
            friend: {
                path: "../../../../assets/icons_128x128/icon_rel_yes.png",
                index: 0,
            },
            noFriend: {
                path: "../../../../assets/icons_128x128/icon_rel_no.png",
                index: 1,
            },
            requestReceived: {
                path: "../../../../assets/icons_128x128/icon_rel_received.png",
                index: 2,
            },
            requestSent: {
                path: "../../../../assets/icons_128x128/icon_rel_send.png",
                index: 3,
            },

        }
    },

    methods: {
        setViewAttributes(set, data=null) {
            // This function sets/unsets the atrributes so that the modals can get the data
            const view = this.domManip.$id("router-view");
            if(set) {
                if (!data) {
                    console.warn("profile: setViewAttributes: data is not defined");
                    return;
                }
                console.log("data:", data);
                // Set the attributes
                view.setAttribute("data-user-id", data.id);
                view.setAttribute("data-user-username", data.username);
                view.setAttribute("data-user-chat-id", data.chatId);
                view.setAttribute("data-relationship", data.relationship);

            } else {
                // Unset the attributes
                view.removeAttribute("data-user-id");
                view.removeAttribute("data-user-username");
                view.removeAttribute("data-user-chat-id");
                view.removeAttribute("data-relationship");
            }

        },

        insertAvatar() {
            const element = this.domManip.$id("avatar");
            element.src = window.origin + '/media/avatars/' + this.result.avatarUrl;
        },

        setupTopLeftButton() {
            if (this.result.relationship.state != "yourself"){
                this.buttonTopLeft.method = this.friendshipMethod;
                this.buttonTopLeft.image = this.buttonSettings[this.result.relationship.state].path;
                if (this.result.relationship.isBlocking) {
                    this.buttonTopLeft.image = "../../../../assets/icons_128x128/icon_rel_block.png";
                }
            }

        },
        setupTopMiddleButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopMiddle.method = this.profileEditMethod;
                this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_edit.png";
            }
            else {
                if (this.result.newMessage)
                    this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_msg_unread.png";
                else
                    this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_msg.png";
                    this.buttonTopMiddle.method = this.messageMethod;
            }
        },
        setupTopRightButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/icons_128x128/icon_logout.png";
                this.buttonTopRight.method = this.logoutMethod;
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/icons_128x128/icon_game_invite.png";
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
            element.src = "../../../../assets/icons_128x128/icon_game_history.png";
            element = this.domManip.$id("button-bottom-right");
            element.src = "../../../../assets/icons_128x128/icon_rel_list.png";
        },

        populateButtons(){
            this.setupTopLeftButton();
            this.setupTopMiddleButton();
            this.setupTopRightButton();
            this.putImagesInButtons();
        },

        blackout() {

            let elements = this.domManip.$queryAll(".blackout, .game-stats-parameters, .progress, .last-seen-image, .button-bottom-left, .button-bottom-right");
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }
        },

        hideElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "none";
        },

        //TODO: this function needs to be removed
        hideModal(modalToHide) {
            let modalElement = this.domManip.$id(modalToHide);
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
        },

        showElement(elementId, flex = null){
            let element = this.domManip.$id(elementId)
            element.style.display = flex || "block";
        },

        profileEditMethod() {
            this.hideElement("edit-profile-modal-avatar-change");
            this.showElement("edit-profile-modal-form");

            this.domManip.$id("edit-profile-modal-form-input-first-name").value = this.result.firstName;
            this.domManip.$id("edit-profile-modal-form-input-last-name").value = this.result.lastName;
            this.domManip.$id("edit-profile-modal-form-input-username").value = this.result.username;
            this.domManip.$id("edit-profile-modal-form-language-selector").value = $store.fromState("locale");


            let modalElement = this.domManip.$id("edit-profile-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

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



        openChatModal() {
            let modalElement = this.domManip.$id("modal-new-conversation");
            const modal = new bootstrap.Modal(modalElement);
            this.domManip.$id("modal-new-conversation-new-chat-text").textContent = translate('profile', "createNewConversation") + this.result.username;
            modal.show();
        },

        messageMethod() {
            if (this.result.chatId)
                router(`/chat`, {id: this.result.chatId});
            else
                this.openChatModal();
        },

        logoutMethod() {
            router("/logout");
        },



        openInviteForGameModal() {
            // Check if the user is already in a game -> redir to game
            call(`game/get-game/${this.routeParams.id}/`, 'GET').then(data => {
                if (data.gameId)
                    router('/game', {"id": data.gameId});
                else {
                    this.domManip.$id("modal-create-game-opponent-photo").src = window.origin + '/media/avatars/' + this.result.avatarUrl;
                    this.domManip.$id("modal-create-game-opponent-name").textContent = this.result.username;
                    let modalElement = this.domManip.$id("modal-create-game");
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                }
            });
        },
        selectMap(chosenMap) {
            const maps = this.domManip.$class("modal-create-game-maps-button");
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

            const data = {
                "mapNumber": this.maps[this.gameSettings.map],
                "powerups": this.gameSettings.powerups,
                "opponentId": this.routeParams.id,
            }
            call('game/create/', 'POST', data).then(data => {
                this.hideModal("modal-create-game");
                router('/game', {"id": data.gameId});
            })
        },

        // TODO: this needs to be removed i  guess
        cancelButton() {
            this.hideModal("modal-edit-friendship");
        },

        powerupsAction() {
            this.gameSettings.powerups = !this.gameSettings.powerups;
        },
    },




    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            WebSocketManager.setCurrentRoute(undefined);
            /* let element = this.domManip.$id("button-top-left");
            this.domManip.$off(element, "click", this.buttonTopLeft.method);
            element = this.domManip.$id("button-top-middle");
            this.domManip.$off(element, "click", this.buttonTopMiddle.method);
            element = this.domManip.$id("button-top-right");
            this.domManip.$off(element, "click", this.buttonTopRight.method);
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
            element = this.domManip.$id("modal-edit-friendship-friendship-primary-button");
            this.domManip.$off(element, "click", this.changeFrendshipPrimaryMethod);
            element = this.domManip.$class("modal-create-game-maps-button");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            element = this.domManip.$id("modal-create-game-powerups-checkbox");
            this.domManip.$off(element, "change", this.powerupsAction);
            element = this.domManip.$id("modal-create-game-start-button");
            this.domManip.$off(element, "click", this.submitInvitation);
            element = this.domManip.$id("modal-edit-friendship-friendship-secondary-button");
            this.domManip.$off(element, "click", this.changeFrendshipSecondaryMethod);
            element = this.domManip.$id("modal-edit-friendship-block-button");
            this.domManip.$off(element, "click", this.changeBlockMethod);
            element = this.domManip.$id("modal-edit-friendship-cancel-button");
            this.domManip.$off(element, "click", this.cancelButton);
            element = this.domManip.$id("modal-new-conversation-create-button");
            this.domManip.$off(element, "click", this.createConversation);
            element = this.domManip.$id("button-bottom-right");
            this.domManip.$off(element, "click", this.openFriendList);
            element = this.domManip.$id("modal-friends-list-search-bar");
            this.domManip.$off(element, "keydown", this.searchFriend); */


            // Unlink the modal buttons to the methods
            modalManager.off("button-top-left", "modal-edit-friendship");
            modalManager.off("button-top-middle", "modal-new-conversation");
            modalManager.off("button-top-right", "modal-create-game");
            modalManager.off("button-bottom-right", "modal-friends-list");
            modalManager.off("test-modal-btn", "modal-template");

            // Remove the attributes from the view
            this.setViewAttributes(false);
        },

        beforeDomInsertion() {
            this.buttonTopLeft.image = undefined;
            this.buttonTopLeft.method = undefined;
        },

        afterDomInsertion() {
			call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                this.result = res;
                WebSocketManager.setCurrentRoute("profile-" + this.result.id);
                console.log(res);
                this.insertAvatar();
                this.setViewAttributes(true, res)
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                    this.blackout();

                // Link the modal buttons to the methods
                modalManager.on("button-top-left", "modal-edit-friendship");
                modalManager.on("button-top-middle", "modal-new-conversation");
                modalManager.on("button-top-right", "modal-create-game");
                modalManager.on("button-bottom-right", "modal-friends-list");
                modalManager.on("test-modal-btn", "modal-template");


/*
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

                let element = this.domManip.$id("edit-profile-modal-form-change-avatar-button");
                this.domManip.$on(element, "click", this.changeAvatarMethod);
                element = this.domManip.$id("edit-profile-modal-avatar-change-upload-button");
                this.domManip.$on(element, "click", this.openFileExplorer);
                element = this.domManip.$id("edit-profile-modal-avatar-change-file-input");
                this.domManip.$on(element, "change", this.extractFile);
                element = this.domManip.$id("edit-profile-modal-avatar-change-crop-image");
                this.domManip.$on(element, "click", this.submitAvatar);
                element = this.domManip.$id("edit-profile-modal-form-submit-button");
                this.domManip.$on(element, "click", this.submitForm);
                element = this.domManip.$id("modal-edit-friendship-friendship-primary-button");
                this.domManip.$on(element, "click", this.changeFrendshipPrimaryMethod);
                element = this.domManip.$class("modal-create-game-maps-button");
                for (let individualElement of element)
                    this.domManip.$on(individualElement, "click", this.selectMap);
                element = this.domManip.$id("modal-create-game-powerups-checkbox");
                this.domManip.$on(element, "change", this.powerupsAction);
                element = this.domManip.$id("modal-create-game-start-button");
                this.domManip.$on(element, "click", this.submitInvitation);
                element = this.domManip.$id("modal-edit-friendship-friendship-secondary-button");
                this.domManip.$on(element, "click", this.changeFrendshipSecondaryMethod);
                element = this.domManip.$id("modal-edit-friendship-block-button");
                this.domManip.$on(element, "click", this.changeBlockMethod);
                element = this.domManip.$id("modal-edit-friendship-cancel-button");
                this.domManip.$on(element, "click", this.cancelButton);
                element = this.domManip.$id("modal-new-conversation-create-button");
                this.domManip.$on(element, "click", this.createConversation);
                element = this.domManip.$id("button-bottom-right");
                this.domManip.$on(element, "click", this.openFriendList);
                element = this.domManip.$id("modal-friends-list-search-bar");
                this.domManip.$on(element, "keydown", this.searchFriend);
                */
            })
            // TODO: on error?
        },
    }
}
