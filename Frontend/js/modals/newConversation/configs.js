import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';

export default {
    attributes: {
        userId: null,
        conversationId: null,
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

        callbackSubmitButton() {
            // This is calling the endpoint to create a new conversation
            const message = this.domManip.$id("modal-new-conversation-textarea").value;
            call("chat/create/conversation/", "POST", {"userId": this.userId, "initialMessage": message}).then(data => {
                $callToast("success", data.message);
                router(`/profile`, {id: this.userId});
            })
        },
    },

    hooks: {
        /*
        This function is called before opening the modal to check if the modal should be opened or not
        In this case: if conversation already exists: Don't open modal but redir to conversation
        */
        async allowedToOpen() {
            let conversationId = this.domManip.$id("router-view").getAttribute("data-user-conversation-id");
            if (conversationId && conversationId !== "null") {
                router(`/chat`, {id: conversationId});
                return false;
            }
            return true;
        },

        beforeOpen () {
            /* This function prepares the modal
                On sucess returns true, on failure returns false
                Will be called by the ModalManager
            */

            // Fetching the attributes from view and store them locally
            try {
                // Try to store userId as Number
                this.userId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
            } catch {
                console.error("newConversationModal: Couldn't find the userId attribute in the view");
                return false;
            }
            if (!this.userId) {
                console.error("newConversationModal: Couldn't find the userId attribute in the view");
                return false;
            }
            this.conversationId = this.domManip.$id("router-view").getAttribute("data-user-conversation-id");
            this.username = this.domManip.$id("router-view").getAttribute("data-user-username");

            // Set modal title
            this.domManip.$id("modal-new-conversation-title").innerText = `Create new conversation with ${this.username}`;
            this.domManip.$id("modal-new-conversation-title").setAttribute("data-user-id", this.userId);

            // Add event listener to the create conversation button
            this.domManip.$on(this.domManip.$id("modal-new-conversation-create-button"), "click", this.callbackSubmitButton.bind(this));
            this.domManip.$on(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));

            this.enableButtonCallback();

            // TODO: set the focus to the textarea
            // Not sure how since this code snippet doesnt fit to our setup...
            // https://getbootstrap.com/docs/4.0/components/modal/#how-it-works

            return true;
        },

        afterClose () {
            this.domManip.$off(this.domManip.$id("modal-new-conversation-create-button"), "click", this.callbackSubmitButton.bind(this));
            this.domManip.$off(this.domManip.$id("modal-new-conversation-textarea"), "input", this.enableButtonCallback.bind(this));
        },
    }
}