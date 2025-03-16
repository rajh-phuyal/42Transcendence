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
import call from '../../abstracts/call.js'
import $callToast from '../../abstracts/callToast.js';
import router from '../../navigation/router.js';

export default {
    attributes: {
        userId: null,
        conversationId: null,
    },

    methods: {

    },

    hooks: {
        /*
        This function is called before opening the modal to check if the modal should be opened or not
        In this case: if conversation already exists: Don't open modal but redir to conversation
        */
        async allowedToOpen() {
            /* TODO: check if torunament is local:
            if yes show modal
            if not just call the endpoint to join the tournament */
        },

        beforeOpen () {
                   },

        afterClose () {

        },
    }
}