import call from '../../abstracts/call.js'
import { $id, $on, $class } from '../../abstracts/dollars.js';
import { populateInfoAndStats } from './script.js';
import { buttonObjects } from "./objects.js"

export default {
    attributes: {
        buttonTopLeft: {
            image: undefined,
            method: undefined,
        },
        buttonTopMiddle: {
            image: undefined,
            method: undefined,
        },
        buttonTopRight: {
            image: undefined,
            method: undefined,
        },
        result: undefined,
        frendshipStateIndex: undefined,
        BlockedState: false,
    },

    methods: {
        populateButtons(){
            // Top left Button
            if (this.result.relationship.state != "yourself")
            {
                this.buttonTopLeft.method = this.friendshipMethod;
                if (this.result.relationship.isBlocking) {
                    this.buttonTopLeft.image = "../../../../assets/profileView/blockedUserIcon.png";
                    this.BlockedState = true;
                }
                else if (this.result.relationship.state == "friend") {
                    this.buttonTopLeft.image = "../../../../assets/profileView/friendsIcon.png";
                    this.frendshipStateIndex = 0;
                }
                else if (this.result.relationship.state == "noFriend") {
                    this.buttonTopLeft.image = "../../../../assets/profileView/firendRequestIcon.png";
                    this.frendshipStateIndex = 1;
                }
                else if (this.result.relationship.state == "requestReceived") {
                    this.buttonTopLeft.image = "../../../../assets/profileView/receivedFriendRequest.png";
                    this.frendshipStateIndex = 2;
                }
                else if (this.result.relationship.state == "requestSent") {
                    this.buttonTopLeft.image = "../../../../assets/profileView/sentFriendRequest.png";
                    this.frendshipStateIndex = 3;
                }
            }

            // Top middle Button
            if (this.result.relationship.state == "yourself") {
                this.buttonTopMiddle.image = "../../../../assets/profileView/penIcon.png";
            }
            else {
                if (this.result.newMessage)
                    this.buttonTopMiddle.image = "../../../../assets/profileView/unreadMessageIcon.png";
                else
                    this.buttonTopMiddle.image = "../../../../assets/profileView/sendMessageIcon.png";
            }

            // Top right Button
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/profileView/logoutIcon.png";
            }
            else {
                if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/profileView/invitePongIcon.png";
                }
            }

            // put images in the buttons
            let element = $id("button-top-left");
            if (this.buttonTopLeft.image)
                element.src = this.buttonTopLeft.image;
            else
                element.style.display = "none";
            element = $id("button-top-middle");
            element.src = this.buttonTopMiddle.image;
            element = $id("button-top-right");
            if (this.buttonTopRight.image)
                element.src = this.buttonTopRight.image;
            else
                element.style.display = "none";
            element = $id("button-bottom-left");
            element.src = "../../../../assets/profileView/gamingHistoryIcon.png";
            element = $id("button-bottom-right");
            element.src = "../../../../assets/profileView/FriendsListIcon.png";
        },

        blackout() {
            let elements = $class("blackout");
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }

            elements = $class("game-stats-parameters");
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }

            elements = $class("progress");
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }

            let element = $id("last-seen-image");
            element.style.display = "none";
            
            element = $id("button-bottom-left");
            element.style.display = "none";

            element = $id("button-bottom-right");
            element.style.display = "none";
            
        },

        friendshipMethod() {

            let element = $id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.frendshipStateIndex].text;

            element = $id("friendship-modal-friendship-primary-button")
            element.textContent = buttonObjects[this.frendshipStateIndex].leftButtonText;

            let modalElement = $id("friendship-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        }

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            console.log(this.routeParams);
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                this.result = res;
                console.log(res);
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                {
                    console.log("is blocked");
                    this.blackout();
                }

                
                
                // callback functions
                let element = $id("button-top-left");
                $on(element, "click", this.buttonTopLeft.method);
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/