import call from '../../abstracts/call.js'
import { populateInfoAndStats } from './script.js';
import router from '../../navigation/router.js';
import WebSocketManager from '../../abstracts/WebSocketManager.js';
import { modalManager } from '../../abstracts/ModalManager.js';
import { EventListenerManager } from '../../abstracts/EventListenerManager.js';

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

        result: null,
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
        /* This function sets/unsets the atrributes so that the modals can get the data */
        setViewAttributes(set) {
            const view = this.domManip.$id("router-view");
            if(set) {
                if (!this.result) {
                    console.warn("profile: setViewAttributes: this.result is not defined");
                    return;
                }
                console.log(this.result);
                // Set the attributes
                view.setAttribute("data-user-id", this.result.id);
                view.setAttribute("data-user-username", this.result.username);
                view.setAttribute("data-user-first-name", this.result.firstName);
                view.setAttribute("data-user-last-name", this.result.lastName);
                view.setAttribute("data-user-language", this.result.language);
                view.setAttribute("data-user-avatar", this.result.avatarUrl);
                view.setAttribute("data-user-conversation-id", this.result.chatId);
                view.setAttribute("data-relationship", JSON.stringify(this.result.relationship));
            } else {
                // Unset the attributes
                view.removeAttribute("data-user-id");
                view.removeAttribute("data-user-username");
                view.removeAttribute("data-user-first-name");
                view.removeAttribute("data-user-last-name");
                view.removeAttribute("data-user-language");
                view.removeAttribute("data-user-avatar");
                view.removeAttribute("data-user-conversation-id");
                view.removeAttribute("data-relationship");
            }
        },

        setupTopLeftButton() {
            if (this.result.relationship.state != "yourself"){
                this.buttonTopLeft.method = "modal-edit-friendship";
                this.buttonTopLeft.image = this.buttonSettings[this.result.relationship.state].path;
                if (this.result.relationship.isBlocking) {
                    this.buttonTopLeft.image = "../../../../assets/icons_128x128/icon_rel_block.png";
                }
            }

        },
        setupTopMiddleButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopMiddle.method = "modal-edit-profile";
                this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_edit.png";
            }
            else {
                if (this.result.newMessage)
                    this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_msg_unread.png";
                else
                    this.buttonTopMiddle.image = "../../../../assets/icons_128x128/icon_msg.png";
                    this.buttonTopMiddle.method = "modal-new-conversation";
            }
        },
        setupTopRightButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/icons_128x128/icon_logout.png";
                this.buttonTopRight.method = "logout";
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/icons_128x128/icon_game_invite.png";
                this.buttonTopRight.method = "modal-create-game";
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

        /* If user is blocked, the page is blacked out */
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


        callbackLogout() {
            router("/logout");
        },
    },




    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
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
            element = this.domManip.$id("modal-create-game-start-button");
            this.domManip.$off(element, "click", this.submitInvitation);
            element = this.domManip.$id("modal-edit-friendship-friendship-secondary-button");
            this.domManip.$off(element, "click", this.changeFrendshipSecondaryMethod);
            element = this.domManip.$id("modal-edit-friendship-block-button");
            this.domManip.$off(element, "click", this.changeBlockMethod);
            element = this.domManip.$id("modal-new-conversation-create-button");
            this.domManip.$off(element, "click", this.createConversation);
            element = this.domManip.$id("button-bottom-right");
            this.domManip.$off(element, "click", this.openFriendList);
            element = this.domManip.$id("modal-friends-list-search-bar");
            this.domManip.$off(element, "keydown", this.searchFriend); */


            // Unlink the modal buttons to the methods
            modalManager.off("button-top-left", this.buttonTopLeft.method)
            modalManager.off("button-top-middle", this.buttonTopMiddle.method)
            if (this.buttonTopRight.method) {
                if (this.buttonTopRight.method == "logout")
                    this.domManip.$off(this.domManip.$id("button-top-right"), "click", this.callbackLogout);
                else
                    modalManager.off("button-top-right", this.buttonTopRight.method);
            }
            modalManager.off("button-bottom-left", "modal-game-history");
            modalManager.off("button-bottom-right", "modal-friends-list");

            // Remove the attributes from the view
            this.setViewAttributes(false);
        },

        beforeDomInsertion() {
            this.buttonTopLeft.image = undefined;
            this.buttonTopLeft.method = undefined;
        },

        afterDomInsertion() {
            console.warn(this.routeParams.id);
            if (!this.routeParams?.id || isNaN(this.routeParams.id)) {
                router('/404');
                return;
            }
			call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                this.result = res;
                this.setViewAttributes(true)
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                    this.blackout();

                // Link the modal buttons to the methods
                if (this.buttonTopLeft.method)
                    modalManager.on("button-top-left", this.buttonTopLeft.method);
                if (this.buttonTopMiddle.method)
                    modalManager.on("button-top-middle", this.buttonTopMiddle.method);
                if (this.buttonTopRight.method) {
                    if (this.buttonTopRight.method == "logout") {
                        // this.domManip.$on(this.domManip.$id("button-top-right"), "click", this.callbackLogout);
                        EventListenerManager.linkEventListener("button-top-right", "profile", "click", this.callbackLogout);
                    }
                    else
                        modalManager.on("button-top-right", this.buttonTopRight.method);
                }
                modalManager.on("button-bottom-left", "modal-game-history");
                modalManager.on("button-bottom-right", "modal-friends-list");
            }).catch(err => {
                console.log(err);
                router("/404", {msg: err.message});
            }
            );
        },
    }
}
