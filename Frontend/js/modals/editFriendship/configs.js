import { modalManager } from '../../abstracts/ModalManager.js';

export default {
    attributes: {

    },

    methods: {
    },

    hooks: {
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