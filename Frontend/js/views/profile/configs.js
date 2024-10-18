import call from '../../abstracts/call.js'
import { $id } from '../../abstracts/dollars.js';

export default {
    attributes: {
        
    },

    methods: {

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                console.log(res);
                let username = $id("username");   
                username.textContent = "Subject: " + res.username;
            })
            // on error?
        },
    }
}