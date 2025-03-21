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
import router from '../../navigation/router.js';
import call from '../../abstracts/call.js';
import $callToast from '../../abstracts/callToast.js';
import { buttonObjects } from "./buttonObjects.js"

export default {
    attributes: {
        relationship: undefined,
        targetId: undefined,
    },

    methods: {
        hideElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "none";
        },

        /* This function sets all actions and text */
        initModal() {
            let blockIndex;
            if (this.relationship.isBlocking)
                blockIndex = "blocked";
            else
                blockIndex = "unblocked";

            // friendship portion of the modal
            let element = this.domManip.$id("modal-edit-friendship-friendship-text")
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
                element = this.domManip.$id("modal-edit-friendship-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }
        },

        changeFrendshipPrimaryMethod() {
            const object = buttonObjects[this.relationship.state];
            const fullUrl = object.Url + this.targetId + "/";

            call(fullUrl, object.method).then(data =>{
                $callToast("success", data.message);
                router('/profile', { id: this.targetId});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        changeFrendshipSecondaryMethod() {
            call(`user/relationship/reject/${this.targetId}/`, "DELETE").then(data =>{
                $callToast("success", data.message);
                router('/profile', { id: this.targetId});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },

        changeBlockMethod() {
            let object;

            if (this.relationship.isBlocking)
                object = buttonObjects["blocked"];
            else
                object = buttonObjects["unblocked"];
            const fullUrl = object.Url + this.targetId + "/";
            call(fullUrl, object.method).then(data =>{
                $callToast("success", data.message);
                router('/profile', { id: this.targetId});
            }).catch((error) => {
                console.error('Error:', error);
            });
        },
    },

    hooks: {
        beforeOpen () {
            // Fetching the attributes from view and store them locally
            try {
                // Try to store userId (wich is the target) as Number
                this.targetId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
            } catch {
                console.error("createGameModal: Couldn't find the targetId ('data-user-id') attribute in the view");
                return false;
            }
            if (!this.targetId) {
                console.error("createGameModal: Couldn't find the targetId ('data-user-id') attribute in the view");
                return false;
            }
            try {
                let attr = this.domManip.$id("router-view").getAttribute("data-relationship");
                if (!attr) {
                    throw new Error("Attribute 'data-relationship' is missing or empty");
                }
                this.relationship = JSON.parse(attr);
                if (!this.relationship) {  // Ensure object is not `null`
                    throw new Error("Parsed object is null");
                }
            } catch (error) {
                console.error("editFriendshipModal: Couldn't find or parse the relationship attribute in the view");
                return false;
            }

            // Set modal title
            this.domManip.$id("modal-edit-friendship-title").textContent = "Edit Friendship"; //Todo: translate

            // Set the modal content according to the relationship
            this.initModal()

            // Add event listener to the buttons
            this.domManip.$on(this.domManip.$id("modal-edit-friendship-friendship-primary-button"), "click", this.changeFrendshipPrimaryMethod);
            this.domManip.$on(this.domManip.$id("modal-edit-friendship-friendship-secondary-button"), "click", this.changeFrendshipSecondaryMethod);
            this.domManip.$on(this.domManip.$id("modal-edit-friendship-block-button"), "click", this.changeBlockMethod);
            return true;
        },

        afterClose () {
            // Add event listener to the buttons
            this.domManip.$off(this.domManip.$id("modal-edit-friendship-friendship-primary-button"), "click", this.changeFrendshipPrimaryMethod);
            this.domManip.$off(this.domManip.$id("modal-edit-friendship-friendship-secondary-button"), "click", this.changeFrendshipSecondaryMethod);
            this.domManip.$off(this.domManip.$id("modal-edit-friendship-block-button"), "click", this.changeBlockMethod);
        }
    }
}