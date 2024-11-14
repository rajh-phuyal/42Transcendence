import call from '../../abstracts/call.js'
import { $id, $on, $queryAll, $off } from '../../abstracts/dollars.js';
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

        buttonSettings: {
            friend: {
                path: "../../../../assets/profileView/friendsIcon.png",
                index: 0,
            },
            noFriend: {
                path: "../../../../assets/profileView/firendRequestIcon.png",
                index: 1,
            },
            requestReceived: {
                path: "../../../../assets/profileView/receivedFriendRequest.png",
                index: 2,
            },
            requestSent: {
                path: "../../../../assets/profileView/sentFriendRequest.png",
                index: 3,
            },
            
        }
    },

    methods: {
        insertAvatar() {
            const element = $id("avatar");
            element.src = 'https://ahok.cool/media/avatars/' + this.result.avatarUrl;
            //element.src = 'https://localhost/media/avatars/' + this.result.avatarUrl;
        },

        setupTopLeftButton() {
            if (this.result.relationship.state != "yourself")
                {
                    this.buttonTopLeft.method = this.friendshipMethod;
                    this.buttonTopLeft.image = this.buttonSettings[this.result.relationship.state].path;
                    this.frendshipStateIndex = this.buttonSettings[this.result.relationship.state].index;
                    if (this.result.relationship.isBlocking) {
                        this.buttonTopLeft.image = "../../../../assets/profileView/blockedUserIcon.png";
                        this.blockerState = true;
                    }
                }
        },
        setupTopMiddleButton() {
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
        },
        setupTopRightButton() {
            if (this.result.relationship.state == "yourself") {
                this.buttonTopRight.image = "../../../../assets/profileView/logoutIcon.png";
                this.buttonTopRight.method = this.logoutMethod;
            }
            else if (this.result.relationship.state == "friend" && !this.result.relationship.isBlocking && !this.result.relationship.isBlocked) {
                this.buttonTopRight.image = "../../../../assets/profileView/invitePongIcon.png";
            }
        },
        putImagesInButtons() {
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
        
        populateButtons(){
            this.setupTopLeftButton();
            this.setupTopMiddleButton();
            this.setupTopRightButton();
            this.putImagesInButtons();
        },

        blackout() {

            let elements = $queryAll(".blackout, .game-stats-parameters, .progress, .last-seen-image, .button-bottom-left, .button-bottom-right")
            for (let element of elements) {
                element.style.backgroundColor = "black";
            }
        },

        hideElement(elementId){
            let element = $id(elementId)
            element.style.display = "none";
        },

        friendshipMethod() {

            let blockIndex;
            if (this.blockerState)
                blockIndex = 5;
            else
                blockIndex = 4;


            // friendship portion of the modal
            let element = $id("friendshp-modal-friendship-text")
            element.textContent = buttonObjects[this.frendshipStateIndex].text;
            if (this.result.relationship.state == "noFriend" && this.result.relationship.isBlocked)
            {
                element.style.display = "none";
                this.hideElement("friendship-modal-friendship-primary-button");
            }

            if (!buttonObjects[this.frendshipStateIndex].secundaryButton)
                this.hideElement("friendship-modal-friendship-secundary-button");

            // blocking portion of the friendshop modal
            if (this.result.relationship.state == "requestReceived" || this.result.relationship.state == "requestSent")
                this.hideElement("friendship-modal-block");

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
			let element = $id("button-top-left");
            $off(element, "click", this.buttonTopLeft.method);
			element = $id("button-top-middle");
            $off(element, "click", this.buttonTopMiddle.method);
			element = $id("button-top-right");
            $off(element, "click", this.buttonTopRight.method);
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
