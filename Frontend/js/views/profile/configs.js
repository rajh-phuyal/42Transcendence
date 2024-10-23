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
                let username = $id("username");   
                username.textContent = "Subject: " + res.username;
                let birthName =$id("birth-name");
                birthName.textContent = "Birth name: " + res.lastName + ", " + res.firstName;
                let lastSeenText =$id("last-seen-text");
                lastSeenText.textContent = "Last seen: " + res.lastLogin;
                let lastSeenImg =$id("last-seen-image");
                lastSeenImg.src = "../../../../assets/onlineIcon.png";
                let language =$id("language");
                language.textContent = "language: " + res.language;
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/