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
import { buttonObjects } from "./objects.js"

export default {
    attributes: {
        relationship: undefined,
    },

    methods: {
        hideElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "none";
        },

        friendshipMethod() {

            let blockIndex;
            if (this.relationship.isBlocking)
                blockIndex = "blocked";
            else
                blockIndex = "unblocked";

            // friendship portion of the modal
            let element = this.domManip.$id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.relationship.state].text;
            if (this.relationship.state == "noFriend" && (this.relationship.isBlocked || this.relationship.isBlocking))
            {
                element.style.display = "none";
                this.hideElement("modal-edit-friendship-friendship-primary-button");
            }

            if (!buttonObjects[this.relationship.state].secondaryButton)
                this.hideElement("modal-edit-friendship-friendship-secondary-button");

            // blocking portion of the friendshop modal
            if (this.relationship.state == "requestReceived" || this.relationship.state == "requestSent")
                this.hideElement("modal-edit-friendship-block");

            else {
                element = this.domManip.$id("friendshp-modal-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }

            let modalElement = this.domManip.$id("modal-edit-friendship");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        changeFrendshipPrimaryMethod() {
            const object = buttonObjects[this.result.relationship.state];
            const fullUrl = object.Url + this.result.id + "/";

            call(fullUrl, object.method).then(data =>{
                this.hideModal("modal-edit-friendship");
                $callToast("success", data.message);
                router('/profile', { id: this.result.id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        changeFrendshipSecondaryMethod() {
            call(`user/relationship/reject/${this.result.id}/`, "DELETE").then(data =>{
                this.hideModal("modal-edit-friendship");
                $callToast("success", data.message);
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
            const fullUrl = object.Url + this.result.id + "/";
            call(fullUrl, object.method).then(data =>{
                this.hideModal("modal-edit-friendship");
                $callToast("success", data.message);
                router('/profile', { id: this.result.id});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },
    },

    hooks: {
        beforeOpen () {
            console.log("beforeOpen of modal-edit-friendship");

            // Fetching the attributes from view and store them locally
            this.relationship = this.domManip.$id("router-view").getAttribute("data-relationship");
            if(this.relationship == undefined){
                console.error("editFriendshipModal: Couldn't find the relationship attribute in the view");
                return false;
            }

            // Set modal title
            this.domManip.$id("modal-edit-friendship-title").textContent = "Edit Friendship (need translation!)"; //Todo: translate

            // Add event listener to the create conversation button
            //TODO: add event listener to the buttons
            //this.domManip.$on(this.domManip.$id("modal-new-conversation-create-button"), "click", this.createConversation.bind(this));
            //this.domManip.$on(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));

            return true;
        },
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
           modalManager.closeModal("modal-edit-friendship");
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {
        },
    }
}