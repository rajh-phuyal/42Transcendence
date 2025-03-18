import call from '../../abstracts/call.js';
import router from '../../navigation/router.js';

export default {
    attributes: {
        userId: undefined,
        data: undefined,
    },

    methods: {
        formatTimestamp(isoTimestamp) {
            return moment(isoTimestamp).format('YYYY-MM-DD h:mm a').replace('am', 'a.m.').replace('pm', 'p.m.');
        },

        cleanUpGameList() {
            let list = this.domManip.$queryAll(".modal-game-history-card");

            for (let element of list) {
                this.domManip.$off(element, "click", this.gameCardClickCallBack);
                element.remove();
            }
        },

        setAvatarOnGameCard (element, playerObject) {
            element.src = `${window.origin}/media/avatars/${playerObject.avatarUrl}`;
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
            // TODO: Create an event listner for the ongoing games @xico what do u mean by this?
        }
    },

    hooks: {
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
                // console.log("data", data);
                this.data = data;
                if (data.games.length)
                    this.domManip.$id("modal-game-history-no-games").style.display = "none";
                for (let element of data.games)
                    this.createGameCard(element);
            })
            return true;
        },

        afterClose () {
            this.cleanUpGameList();
        }
    }
}