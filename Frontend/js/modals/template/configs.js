import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {

    },

    methods: {
    },

    hooks: {
        beforeOpen () {
            // This function prepares the modal
            // On sucess returns true, on failure returns false
            // Will be called by the ModalManager
            return true;
        },
        beforeRouteEnter() {
        },

        beforeRouteLeave() {
            modalManager.closeModal("modal-template");
        },

        beforeDomInsertion() {
        },

        afterDomInsertion() {
        },
    }
}