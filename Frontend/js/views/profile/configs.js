import call from '../../abstracts/call.js'
import { $id, $on, $class } from '../../abstracts/dollars.js';
import { populateInfoAndStats } from './script.js';
import { buttonObjects } from "./objects.js"
import router from '../../navigation/router.js';

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
        blockerState: false,
    },

    methods: {
        insertAvatar() {
            const element = $id("avatar");
            element.src = 'https://localhost/media/avatars/' + this.result.avatarUrl;
        },
        populateButtons(){
            // Top left Button
            if (this.result.relationship.state != "yourself")
            {
                this.buttonTopLeft.method = this.friendshipMethod;
                if (this.result.relationship.state == "friend") {
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
                if (this.result.relationship.isBlocking) {
                    this.buttonTopLeft.image = "../../../../assets/profileView/blockedUserIcon.png";
                    this.blockerState = true;
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
                    this.buttonTopMiddle.method = this.messageMethod;
            }

            // Top right Button
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/profileView/logoutIcon.png";
                this.buttonTopRight.method = this.logoutMethod;
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/profileView/invitePongIcon.png";
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

            console.log("friendship index", this.frendshipStateIndex);
            let blockIndex;
            if (this.blockerState)
                blockIndex = 5;
            else
                blockIndex = 4;

            let element = $id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.frendshipStateIndex].text;


            if (!buttonObjects[this.frendshipStateIndex].secundaryButton) {
                element = $id("friendship-modal-friendship-secundary-button")
                element.style.display = "none";
            }

            if (this.result.relationship.state == "requestReceived" || this.result.relationship.state == "requestSent") {
                element = $id("friendship-modal-block")
                element.style.display = "none";
            }
            else {
                element = $id("friendshp-modal-block-text")
                element.textContent = buttonObjects[blockIndex].text;
            }

            

            let modalElement = $id("friendship-modal");
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        },

        messageMethod() {
            router("/chat");
        },
        
        logoutMethod() {
            router("/logout");
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
                this.insertAvatar();
                populateInfoAndStats(res);
                this.populateButtons();
                if (res.relationship.isBlocked)
                {
                    console.log("is blocked");
                    this.blackout();
                }

                
                
                // callback functions
                if (this.buttonTopLeft.method) {
                    let element = $id("button-top-left");
                    $on(element, "click", this.buttonTopLeft.method);
                }
                if (this.buttonTopMiddle.method) {
                    let element = $id("button-top-middle");
                    $on(element, "click", this.buttonTopMiddle.method);
                }
                if (this.buttonTopRight.method) {
                    let element = $id("button-top-right");
                    $on(element, "click", this.buttonTopRight.method);
                }
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/