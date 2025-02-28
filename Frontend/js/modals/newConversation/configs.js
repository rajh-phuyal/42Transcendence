import { modalManager } from '../../abstracts/ModalManager.js';
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';

export default {
    attributes: {
        userId: null,
    },

    methods: {
        enableButtonCallback() {
            // Enable the button if the input is not empty
            const input = this.domManip.$id("modal-new-conversation-textarea");
            const btn = this.domManip.$id("modal-new-conversation-create-button");
            if (input.value.trim() === "")
                btn.disabled = true;
            else
                btn.disabled = false;
        },

        createConversation() {
            // This is calling the endpoint to create a new conversation
            console.log("1");
            const message = this.domManip.$id("modal-new-conversation-textarea").value;
            console.log("2");
            call("chat/create/conversation/", "POST", {"userId": this.userId, "initialMessage": message}).then(data => {
                console.log("3");
                $callToast("success", data.message);
                console.log("4");
                router(`/profile`, {id: this.userId});
                console.log("5");
            })
        },
    },

    hooks: {
        beforeOpen () {
            // This function prepares the modal
            // On sucess returns true, on failure returns false
            // Will be called by the ModalManager

            console.log("Running beforeOpen hook for modal-new-conversation");
            // Fetching the attributes from view and store them locally


            // Try to store userId as Number
            try {
                this.userId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
            } catch {
                console.error("newConversationModal: Couldn't find the userId attribute in the view");
                return false;
            }
            if (!this.userId) {
                console.error("newConversationModal: Couldn't find the userId attribute in the view");
                return false;
            }
            this.chatId = this.domManip.$id("router-view").getAttribute("data-user-chat-id");
            this.username = this.domManip.$id("router-view").getAttribute("data-user-username");
            // If already a chat exists, redirect to the chat
            if(this.chatId && this.chatId !== "null") {
                router(`/chat`, {id: this.chatId});
                return false;
            }



            // Set modal title
            this.domManip.$id("modal-new-conversation-title").innerText = `Create new conversation with ${this.username}`;
            this.domManip.$id("modal-new-conversation-title").setAttribute("data-user-id", this.userId);

            // Add event listener to the create conversation button
            this.domManip.$on(this.domManip.$id("modal-new-conversation-create-button"), "click", this.createConversation.bind(this));
            this.domManip.$on(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));

            // TODO: set the focus to the textarea
            // Not sure how since this code snippet doesnt fit topur setup...
            // https://getbootstrap.com/docs/4.0/components/modal/#how-it-works

            return true;
        },
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            modalManager.closeModal("modal-new-conversation");
            this.domManip.$off(this.domManip.$id("modal-new-conversation-create-button"), "click", this.createConversation.bind(this));
            this.domManip.$off(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {

        },
    }
}