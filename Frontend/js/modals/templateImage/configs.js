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
        async allowedToOpen() {
            return false;
        },

        beforeOpen () {
        },

        afterClose () {
        }
    }
}