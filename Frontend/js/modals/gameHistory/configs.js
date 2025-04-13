import call from '../../abstracts/call.js';
import { loadTimestamp } from '../../abstracts/timestamps.js';
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';
import $callToast from '../../abstracts/callToast.js';

export default {
    attributes: {
        userId: undefined,
        username: undefined,
        data: undefined,
        opponents: [],
    },

    methods: {
        translateElements() {
            this.domManip.$id("modal-game-history-search-bar").placeholder = translate("gameHistory", "placeholderFilter");
        },

        formatTimestamp(isoTimestamp) {
            return loadTimestamp(isoTimestamp, "YY-MM-DD hh:mm");
        },

        cleanUpGameList() {
            let list = this.domManip.$queryAll(".modal-game-history-card");

            for (let element of list) {
                this.domManip.$off(element, "click", this.gameCardClickCallBack);
                element.remove();
            }
        },

        setAvatarOnGameCard (element, playerObject) {
            element.src = `${window.origin}/media/avatars/${playerObject.avatar}`;
            if (playerObject.result === "lost")
                element.style.filter = "brightness(50%)";
        },

        gameCardClickCallBack(event) {
            // console.log("event:", event.srcElement.parentElement);
            let gameId = event.srcElement.getAttribute("game-id");
            if (gameId == null)
                gameId = event.srcElement.parentElement.getAttribute("game-id");
            // console.log("game id:", gameId);
            router('/game',  { id: gameId });
        },

        createGameCard(gameObject) {
            const template = this.domManip.$id("modal-game-history-card-template").content.cloneNode(true);
            const container = template.querySelector(".modal-game-history-card");

            container.setAttribute("game-id", gameObject.id);

            if (!this.username)
                this.username = gameObject.playerLeft.id === this.userId ? gameObject.playerLeft.username : gameObject.playerRight.username;
            const opponent = gameObject.playerRight.id === this.userId ? gameObject.playerLeft.username : gameObject.playerRight.username;

            if (!this.opponents.includes(opponent))
                this.opponents.push(opponent);

            this.domManip.$addClass(container, `${this.username}-${opponent}`);

            this.domManip.$on(container, "click", this.gameCardClickCallBack);

            this.setAvatarOnGameCard(container.querySelector(".modal-game-history-card-playerLeft-avatar"), gameObject.playerLeft);
            this.setAvatarOnGameCard(container.querySelector(".modal-game-history-card-playerRight-avatar"), gameObject.playerRight);

            container.querySelector(".modal-game-history-card-playerLeft-username").textContent = gameObject.playerLeft.username;
            container.querySelector(".modal-game-history-card-playerRight-username").textContent = gameObject.playerRight.username;
            container.querySelector(".modal-game-history-card-score").textContent = `${gameObject.playerLeft.points}-${gameObject.playerRight.points}`;

            if (gameObject.finishTime)
                container.querySelector(".modal-game-history-card-date").textContent = this.formatTimestamp(gameObject.finishTime);
            else
                container.querySelector(".modal-game-history-card-date").textContent = gameObject.state;
            this.domManip.$id("modal-game-history-game-list-container").appendChild(container);
        },
        searchBarTypeListener() {
            const searchBarElement = this.domManip.$id("modal-game-history-search-bar")
            let inputValue = searchBarElement.value.trim();

            const gameCards = this.domManip.$class("modal-game-history-card");
            for (let element of gameCards)
                element.style.display = 'none';

            this.domManip.$id("modal-game-list-list-result-not-found-message").style.display = 'none';
            const filteredArray =  this.opponents.filter(value => value.startsWith(inputValue));
            if (!filteredArray.length)
                this.domManip.$id("modal-game-list-list-result-not-found-message").style.display = 'flex';

            for (let names of filteredArray) {
                const elementsToFilter = this.domManip.$class(`${this.username}-${names}`)
                for (let element of elementsToFilter)
                    element.style.display = 'grid';
            }
        }
    },

    hooks: {
        async allowedToOpen() {
            // If the parent view is the profile, we need to check if the target has blocked the client
            /* If target blocked u don,t open modal */
            try {
                let dataRel = this.domManip.$id("router-view").getAttribute("data-relationship");
                dataRel = JSON.parse(dataRel);
                if (!dataRel) {
                    throw new Error("Attribute 'data-relationship' is missing or empty");
                }
                if(dataRel && dataRel?.isBlocked) {
                    $callToast("error", translate("profile", "blocked"));
                    return false;
                }
            } catch (error) {
                //console.log("Not a problem since we are not on the profile view - I hope");
            }
            return true;
        },
        beforeOpen () {
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
            call(`game/history/${this.userId}/`, 'GET').then(data => {
                this.data = data;
                this.translateElements();
                if (!data.games.length) {
                    this.domManip.$id("modal-game-history-no-games").style.display = "block";
                    return ;
                }
                this.domManip.$id("modal-game-history-no-games").style.display = "none";
                for (let element of data.games)
                    this.createGameCard(element);
            })
            this.domManip.$on(this.domManip.$id("modal-game-history-search-bar"), "input", this.searchBarTypeListener);
            return true;
        },

        afterClose () {
            this.cleanUpGameList();
            this.domManip.$off(this.domManip.$id("modal-game-history-search-bar"), "input", this.searchBarTypeListener);
        }
    }
}