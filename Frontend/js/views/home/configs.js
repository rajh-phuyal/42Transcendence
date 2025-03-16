import { $id, $on, $off, $class } from '../../abstracts/dollars.js';
import { mouseClick, isHovering, buildCanvas } from './script.js'
import canvasData from './data.js'
import call from '../../abstracts/call.js'
import callToast from '../../abstracts/callToast.js'

export default {
    attributes: {

        //TODO: place this map in the store
        maps: {
            "ufo": 1,
            "lizard-people": 2,
            "snowman": 3,
            "lochness": 4,
        },

        tournament: {
            type: "public",
            map: "random",
            userIds: [],
        },

        users: [
            { id: 13, avatar: '../../../assets/avatars/dd6e8101-fde8-469a-97dc-6b8bb9e8296e.png', username: "rajh" },
            { id: 11, avatar: "../../../assets/avatars/73d3a3c0-f3ef-43a1-bdce-d798cb286f27.png", username: "alex" },
            { id: 10, avatar: "../../../assets/avatars/4d39f530-68c8-42eb-ad28-45445424da5b.png", username: "ale" },
            { id: 18, avatar: '../../../assets/avatars/1e3751c5-5e47-45f2-9967-111fd26a6be8.png', username: "anatolii" },
            { id: 12, avatar: "../../../assets/avatars/fe468ade-12ed-4045-80a7-7d3e45be997e.png", username: "xico" },
        ]
    },

    methods: {

        createTournament() {
            const tournamentName = this.domManip.$id("tournament-modal-create-form-name-container-input").value;
            const powerups = this.domManip.$id("tournament-modal-create-form-name-container-checkbox").checked;
            if (this.tournament.map == "random") {
                this.tournament.map = parseInt(Math.random() * (4 - 1) + 1);
            }
            else
            this.tournament.map = this.maps[this.tournament.map]

            call('tournament/create/', "POST", {
                "name": tournamentName,
                "localTournament": this.tournament.type === "local",
                "publicTournament": this.tournament.type === "public",
                "mapNumber": this.tournament.map,
                "opponentIds": this.tournament.type !== "public" ? this.tournament.userIds : [],
                "powerups": powerups
            }).then(data => {
                callToast("success", data.message);
                this.router(`/tournament`, { id: data.tournamentId });
            }).catch(error => {
                callToast("error", error.message);
            });
        },

        selectMap(chosenMap) {
            const maps = this.domManip.$class("tournament-modal-create-maps-button");
            this.tournament.map = chosenMap.srcElement.name
            for (let element of maps) {
                if (element.name != this.tournament.map)
                    element.style.opacity = 0.7;
                else
                    element.style.opacity = 1;
            }
        },

        selectTournamentType(chosenType) {
            const type = this.domManip.$class("tournament-modal-create-form-type-buttons");
            this.tournament.type = chosenType.srcElement.getAttribute("type");
            if (this.tournament.type != "public")
                this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").style.display = "flex";
            else
                this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").style.display = "none";

            for (let element of type) {
                if (element.getAttribute("type") != this.tournament.type)
                    element.setAttribute('highlight', 'false');
                else
                    element.setAttribute('highlight', 'true');
                ;
            }
        },

        deleteInviteUserCard(event) {

            const userId = event.target.parentNode.getAttribute("userId");
            this.tournament.userIds = this.tournament.userIds.filter((element) => element != userId);
            event.target.parentNode.remove();

        },

        createInviteUserCard(userObject) {
			const { user } = userObject;
            if (this.tournament.userIds.find(id => id === user.id))
                return;
            this.tournament.userIds.push(user.id);

            let template = $id("template-tournament-modal-create-form-invited-user-card").content.cloneNode(true);

            const container = template.querySelector(".tournament-modal-create-form-invited-user-card");
            container.setAttribute("userId", user.id);
            template.querySelector(".tournament-modal-create-form-invited-user-card-avatar").src = window.location.origin + "/media/avatars/" + user.avatar_path;
            template.querySelector(".tournament-modal-create-form-invited-user-card-username").textContent = user.username;
            this.domManip.$on(template.querySelector(".tournament-modal-create-form-invited-user-card-delete-user"), "click", this.deleteInviteUserCard);
            this.domManip.$id("template-tournament-modal-create-form-invited-user-card-container").appendChild(container);

        },

        selectUserToInvite(event) {
            const user = event.detail;
            console.log("user", user);
            this.createInviteUserCard(user);
        },

        fetchAvailableTournaments() {
            call('tournament/to-join/', "GET").then(data => {
                setTimeout(() => {
                    const container = this.domManip.$id("tournament-modal-join-tournament-cards-container");
                    container.innerHTML = "";
                    for (let tournament of data.tournaments) {
                        this.createJoinTournamentCard(tournament);
                    }
                }, 500); // let the DOM be mounted first
            });
        },

        toggleCreateJoinView() {
            const createTournament = $id("tournament-modal-create-container");
            const joinTournament = $id("tournament-modal-join-container");
            const displaySwitch = {
                flex: "none",
                none: "flex"
            };
            createTournament.style.display = displaySwitch[window.getComputedStyle(createTournament, null).display];
            joinTournament.style.display = displaySwitch[window.getComputedStyle(joinTournament, null).display];

            if (window.getComputedStyle(joinTournament, null).display === "flex") {
                const container = this.domManip.$id("tournament-modal-join-tournament-cards-container");
                container.innerHTML = `<p class="tournament-modal-join-tournament-cards-container-loading"> Loading...</p>`;
                this.fetchAvailableTournaments();
            }
        },

        redirectTournamentLobby(event) {
            // then redirect to the tournament lobby
            const tournamentId = event.target.parentNode.getAttribute("tournamentId");
            this.router(`/tournament`, { id: tournamentId });
        },

        createJoinTournamentCard(tournamentObject) {
            let template = this.domManip.$id("tournament-modal-join-tournament-cards-template").content.cloneNode(true);

            const container = template.querySelector(".tournament-modal-join-tournament-card");
            container.setAttribute("tournamentId", tournamentObject.tournamentId);

            const nameElement = container.querySelector(".tournament-modal-join-tournament-name");
            if (nameElement) {
                nameElement.textContent = tournamentObject.tournamentName;
            }

            this.domManip.$on(container, "click", this.redirectTournamentLobby);
            this.domManip.$id("tournament-modal-join-tournament-cards-container").appendChild(container);
        },

		escapeCallback(event) {
			console.log("key pressed", event.key);
			if (event.key === "Escape") {
				const modal = this.domManip.$id("home-modal");
				if (modal) {
					modal.classList.add("custom-modal");
				}
			}
		},

        playAgainstAI() {
            call("game/create/", "POST", {
                "mapNumber": 1,
                "powerups": true,
                "opponentId": 2 // AI
            }).then(data => {
                this.router(`/game`, { id: data.gameId });
            }).catch(error => {
                callToast("error", error.message);
            });
        },
    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {
            $off(window, "select-user-invite", this.selectUserToInvite);
            // Close the modal properly using Bootstrap's modal API before leaving
            const tournamentModal = bootstrap.Modal.getInstance(this.domManip.$id("home-modal"));
            if (tournamentModal) {
                tournamentModal.hide();
            }
			const homeModal = this.domManip.$id("home-modal");
			if (homeModal)
				homeModal.classList.add("custom-modal");

            const aiModal = this.domManip.$id("AI-modal");
            if (aiModal) {
                aiModal.classList.add("custom-modal");
            }

            $off(document, "click", mouseClick);
            $off(document, "mousemove", isHovering);
			$off(this.domManip.$id('home-view'), "keydown", this.escapeCallback);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            if (element)
                this.domManip.$off(element, "click", this.createTournament);
            element = this.domManip.$id("ai-modal-start-button");
            if (element)
                this.domManip.$off(element, "click", this.playAgainstAI);

            element = this.domManip.$class("tournament-modal-create-maps-button");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            element = this.domManip.$class("tournament-modal-create-form-type-buttons");
            for (let individualElement of element)
                this.domManip.$off(individualElement, "click", this.selectMap);
            this.domManip.$off(this.domManip.$id("tournament-modal-create-form-join-button"), "click", this.toggleCreateJoinView);
            this.domManip.$off(this.domManip.$id("tournament-modal-join-form-host-button"), "click", this.toggleCreateJoinView);
        },

        beforeDomInsertion() {

            this.tournament.type = "public";
            this.tournament.map = "random";
            this.tournament.userIds = [];
        },

        afterDomInsertion() {
            // stores the id of the element currently highlighted
            canvasData.highlitedImageID = 0;

            // Get the canvas element and its context
            canvasData.canvas = $id("home-canvas");
            let canvas = canvasData.canvas;

            canvasData.context = canvas.getContext('2d');

            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            // Adjust the pixel ratio so it draws the images with higher resolution
            const scale = window.devicePixelRatio;

            canvasData.context.imageSmoothingEnabled = true;
            canvasData.context.scale(scale, scale);

            // build thexport e first frame
            buildCanvas();

			const homeView = $id('home-view');
			$on(homeView, "keydown", this.escapeCallback);

            // for (let element of this.users)
                // this.createInviteUserCard(element);

            $on(document, "click", mouseClick);
            $on(document, "mousemove", isHovering);
            let element = this.domManip.$id("tournament-modal-create-form-create-button");
            this.domManip.$on(element, "click", this.createTournament);
            this.domManip.$on(this.domManip.$id("tournament-modal-create-form-join-button"), "click", this.toggleCreateJoinView);
            this.domManip.$on(this.domManip.$id("tournament-modal-join-form-host-button"), "click", this.toggleCreateJoinView);
            element = this.domManip.$class("tournament-modal-create-maps-button");
            for (let individualElement of element)
                this.domManip.$on(individualElement, "click", this.selectMap);
            element = this.domManip.$class("tournament-modal-create-form-type-buttons");
            for (let individualElement of element)
                this.domManip.$on(individualElement, "click", this.selectTournamentType);
            element = this.domManip.$id("ai-modal-start-button");
            if (element)
                this.domManip.$on(element, "click", this.playAgainstAI);
            // for the search bar
            this.domManip.$on(window, "select-user-invite", this.selectUserToInvite);
        },
    }
}