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
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        userId: null,
        friendList: undefined,

        buttonSettings: {
            friend: {
                path: "../../../../assets/icons_128x128/icon_rel_yes.png",
                index: 0,
            },
            noFriend: {
                path: "../../../../assets/icons_128x128/icon_rel_no.png",
                index: 1,
            },
            requestReceived: {
                path: "../../../../assets/icons_128x128/icon_rel_received.png",
                index: 2,
            },
            requestSent: {
                path: "../../../../assets/icons_128x128/icon_rel_send.png",
                index: 3,
            },

        }
    },

    methods: {
        hideElement(elementId){
            let element = this.domManip.$id(elementId)
            element.style.display = "none";
        },

        showElement(elementId, flex = null){
            let element = this.domManip.$id(elementId)
            element.style.display = flex || "block";
        },

        clickFriendCard(event) {
            let element = event.srcElement.getAttribute("user-id");
            if (element == null)
                element = event.srcElement.parentElement.getAttribute("user-id");
            router('/profile',  { id: element });
        },

        // Create the friend list elements and populate the list; Also add event listeners to the cards
        populateFriendList() {
            const mainDiv = this.domManip.$id("modal-friends-list-list");
            for (let element of this.friendList){
                const container = this.domManip.$id("modal-friends-list-list-element-template").content.cloneNode(true);
                const elementDiv = container.querySelector(".modal-friends-list-list-element");
                elementDiv.setAttribute("user-id", element.id);
                elementDiv.setAttribute("id", "modal-friends-list-list-element-user-" + element.username);

                container.querySelector("#modal-friends-list-list-element-avatar-image").src = window.origin + '/media/avatars/' + element.avatarUrl;
                container.querySelector(".modal-friends-list-list-element-username").textContent = element.username;
                container.querySelector("#modal-friends-list-list-element-friendship-image").src = this.buttonSettings[element.status].path;
                mainDiv.appendChild(container)
                this.domManip.$on(elementDiv, "click", this.clickFriendCard);
            }
        },

        // Main Function to fetch the friend list from the server and populate the list
        fetchFriendList() {

            call(`/user/friend/list/${this.userId}/`, "GET").then((res) => {
                // console.log("Fetching friend list");
                this.removeFriendsList();
                // console.log("Removed old friend list");
                this.friendList = res.friends;
                this.populateFriendList();
                // console.log("Populated new friend list");
                this.domManip.$id("modal-friends-list-search-bar").value = "";
                this.hideElement("modal-friends-list-list-result-not-found-message");
            }).catch((error) => {
                console.error('Error:', error);
            });

        },

        // Remove all friend list elements from the list and remove the event listeners
        removeFriendsList() {
            if (!this.friendList)
                return ;
            for (let user of this.friendList)
            {
                const elementId = "modal-friends-list-list-element-user-" + user.username;
                const element =  this.domManip.$id(elementId);
                this.domManip.$off(element, "click", this.clickFriendCard);
                element.remove();
            }
            this.friendList = undefined;
        },

        // This is the Event Listener for the search bar typing
        searchBarTypeListener(event) {
            const searchBarElement = this.domManip.$id("modal-friends-list-search-bar")
            let inputValue = searchBarElement.value.trim();

            for (let element of this.friendList) {
                this.showElement("modal-friends-list-list-element-user-" + element.username, "flex");
            }
            this.hideElement("modal-friends-list-list-result-not-found-message");

            const filteredObj = Object.fromEntries(
                Object.entries(this.friendList).filter(([key, value]) => !value.username.startsWith(inputValue))
            );

            if (Object.values(filteredObj).length === this.friendList.length)
                this.showElement("modal-friends-list-list-result-not-found-message");

            for (let [key, element] of Object.entries(filteredObj)) {
                this.hideElement("modal-friends-list-list-element-user-" + element.username);
            }
        },
    },

    hooks: {
        beforeOpen () {
            // console.log("beforeOpen of modal-friend-list");
            // Fetching the attributes from view and store them locally
            try {
                // Try to store userId as Number
                this.userId = parseInt(this.domManip.$id("router-view").getAttribute("data-user-id"));
            } catch {
                console.error("friendListModal: Couldn't find the userId attribute in the view");
                return false;
            }
            if (!this.userId) {
                console.error("friendListModal: Couldn't find the userId attribute in the view");
                return false;
            }
            // Set modal title
            this.domManip.$id("modal-friends-list-title").innerText = translate("friendsList", "title");
            // Load the friend list
            this.fetchFriendList();
            // Add event listener to the search bar
            const searchBar = this.domManip.$id("modal-friends-list-search-bar");
            this.domManip.$on(searchBar, "input", this.searchBarTypeListener);
            return true;
        },

        afterClose () {
            this.removeFriendsList();
            // Remove event listener from the search
            const searchBar = this.domManip.$id("modal-friends-list-search-bar");
            this.domManip.$off(searchBar, "input", this.searchBarTypeListener);
        }
    }
}