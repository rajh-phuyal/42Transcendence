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
    },

    hooks: {
        beforeOpen () {
            console.log("beforeOpen of modal-create-game");

            // Fetching the attributes from view and store them locally
//            this.relationship = this.domManip.$id("router-view").getAttribute("data-relationship");
//            if(this.relationship == undefined){
//                console.error("editFriendshipModal: Couldn't find the relationship attribute in the view");
//                return false;
//            }
//
//            // Set modal title
//            this.domManip.$id("modal-edit-friendship-title").textContent = "Edit Friendship (need translation!)"; //Todo: translate
//
//            // Add event listener to the create conversation button
//            //TODO: add event listener to the buttons
//            //this.domManip.$on(this.domManip.$id("modal-new-conversation-create-button"), "click", this.createConversation.bind(this));
//            //this.domManip.$on(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));
//
            return true;
        },
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            modalManager.closeModal("modal-create-game");
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {
        },
    }
}