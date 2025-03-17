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


import call from '../../abstracts/call.js'
import callToast from '../../abstracts/callToast.js'
import { modalManager } from '../../abstracts/ModalManager.js';

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
            const tournamentName = this.domManip.$id("modal-tournament-create-form-name-container-input").value;
            const powerups = this.domManip.$id("modal-tournament-create-form-name-container-checkbox").checked;
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
            const maps = this.domManip.$class("modal-tournament-create-maps-button");
            this.tournament.map = chosenMap.srcElement.name
            for (let element of maps) {
                if (element.name != this.tournament.map)
                    element.style.opacity = 0.7;
                else
                    element.style.opacity = 1;
            }
        },



        selectTournamentType(chosenType) {
            const type = this.domManip.$class("modal-tournament-create-form-type-buttons");
            this.tournament.type = chosenType.srcElement.getAttribute("type");
            if (this.tournament.type != "public")
                this.domManip.$id("template-modal-tournament-create-form-invited-user-card-container").style.display = "flex";
            else
                this.domManip.$id("template-modal-tournament-create-form-invited-user-card-container").style.display = "none";

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

            let template = this.domManip.$id("template-modal-tournament-create-form-invited-user-card").content.cloneNode(true);

            const container = template.querySelector(".modal-tournament-create-form-invited-user-card");
            container.setAttribute("userId", user.id);
            template.querySelector(".modal-tournament-create-form-invited-user-card-avatar").src = window.location.origin + "/media/avatars/" + user.avatar_path;
            template.querySelector(".modal-tournament-create-form-invited-user-card-username").textContent = user.username;
            this.domManip.$on(template.querySelector(".modal-tournament-create-form-invited-user-card-delete-user"), "click", this.deleteInviteUserCard);
            this.domManip.$id("template-modal-tournament-create-form-invited-user-card-container").appendChild(container);

        },

        selectUserToInvite(event) {
            const user = event.detail;
            console.log("user", user);
            this.createInviteUserCard(user);
        },

        fetchAvailableTournaments() {
            call('tournament/to-join/', "GET").then(data => {
                setTimeout(() => {
                    const container = this.domManip.$id("modal-tournament-join-tournament-cards-container");
                    container.innerHTML = "";
                    for (let tournament of data.tournaments) {
                        this.createJoinTournamentCard(tournament);
                    }
                }, 500); // let the DOM be mounted first
            });
        },

        toggleCreateJoinView() {
            const createTournament = this.domManip.$id("modal-tournament-create-container");
            const joinTournament = this.domManip.$id("modal-tournament-join-container");
            const displaySwitch = {
                flex: "none",
                none: "flex"
            };
            createTournament.style.display = displaySwitch[window.getComputedStyle(createTournament, null).display];
            joinTournament.style.display = displaySwitch[window.getComputedStyle(joinTournament, null).display];

            if (window.getComputedStyle(joinTournament, null).display === "flex") {
                const container = this.domManip.$id("modal-tournament-join-tournament-cards-container");
                container.innerHTML = `<p class="modal-tournament-join-tournament-cards-container-loading"> Loading...</p>`;
                this.fetchAvailableTournaments();
            }
        },

        redirectTournamentLobby(event) {
            // then redirect to the tournament lobby
            const tournamentId = event.target.parentNode.getAttribute("tournamentId");
            this.router(`/tournament`, { id: tournamentId });
        },

        createJoinTournamentCard(tournamentObject) {
            let template = this.domManip.$id("modal-tournament-join-tournament-cards-template").content.cloneNode(true);

            const container = template.querySelector(".modal-tournament-join-tournament-card");
            container.setAttribute("tournamentId", tournamentObject.tournamentId);

            const nameElement = container.querySelector(".modal-tournament-join-tournament-name");
            if (nameElement) {
                nameElement.textContent = tournamentObject.tournamentName;
            }

            this.domManip.$on(container, "click", this.redirectTournamentLobby);
            this.domManip.$id("modal-tournament-join-tournament-cards-container").appendChild(container);
        }
    },

    hooks: {
        beforeOpen() {
            //modalManager.hideModal("modal-tournament");
            //modalManager.on("test-test", "modal-create-game");
           // this.tournament.type = "public";
           // this.tournament.map = "random";
           // this.tournament.userIds = [];
             // TODO:
            //this.domManip.$on(this.domManip.$id("modal-tournament-create-form-join-button"), "click", this.toggleCreateJoinView);
            //this.domManip.$on(this.domManip.$id("modal-tournament-join-form-host-button"), "click", this.toggleCreateJoinView);
            //element = this.domManip.$class("modal-tournament-create-maps-button");
            //for (let individualElement of element)
            //    this.domManip.$on(individualElement, "click", this.selectMap);
            //element = this.domManip.$class("modal-tournament-create-form-type-buttons");
            //for (let individualElement of element)
            //    this.domManip.$on(individualElement, "click", this.selectTournamentType);
//
            //// for the search bar
            //this.domManip.$on(window, "select-user-invite", this.selectUserToInvite);
            return true;
        },

        afterClose () {
            // TODO:
            //let element = this.domManip.$id("modal-tournament-create-form-create-button");
            //if (element)
            //    this.domManip.$off(element, "click", this.createTournament);
            //element = this.domManip.$class("modal-tournament-create-maps-button");
            //for (let individualElement of element)
            //    this.domManip.$off(individualElement, "click", this.selectMap);
            //element = this.domManip.$class("modal-tournament-create-form-type-buttons");
            //for (let individualElement of element)
            //    this.domManip.$off(individualElement, "click", this.selectMap);
            //this.domManip.$off(this.domManip.$id("modal-tournament-create-form-join-button"), "click", this.toggleCreateJoinView);
            //this.domManip.$off(this.domManip.$id("modal-tournament-join-form-host-button"), "click", this.toggleCreateJoinView);
        }
    }
}