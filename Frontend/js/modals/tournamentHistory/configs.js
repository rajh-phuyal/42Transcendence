import { modalManager } from '../../abstracts/ModalManager.js';
import $store from '../../store/store.js'
import call from '../../abstracts/call.js'

export default {
    attributes: {

    },

    methods: {
        formatTimestamp(isoTimestamp) {
            return moment(isoTimestamp).format('YYYY-MM-DD h:mm a').replace('am', 'a.m.').replace('pm', 'p.m.');
        },

        cleanUpTournamentList() {
            let list = this.domManip.$queryAll(".modal-tournament-history-card");

            for (let element of list) {
                this.domManip.$off(element, "click", this.gameCardClickCallBack); /////////////////////////////////
                element.remove();
            }
        },

        tournamentCardClickCallBack(event) {
            // console.log("event:", event.srcElement.parentElement);
            let tournamentId = event.srcElement.getAttribute("tournament-id");
            if (tournamentId == null)
                tournamentId = event.srcElement.parentElement.getAttribute("tournament-id");
            // console.log("tournament id:", tournamentId);
            router('/tournament',  { id: tournamentId });
        },

        createTournamentCard(tournamentObject) {
            const template = this.domManip.$id("modal-tournament-history-card-template").content.cloneNode(true);
            const container = template.querySelector(".modal-tournament-history-card");

            container.setAttribute("tournament-id", tournamentObject.id);

            this.domManip.$on(container, "click", this.tournamentCardClickCallBack);

            container.querySelector(".modal-tournament-history-card-tournament-name").textContent = tournamentObject.name;

            if (tournamentObject.public)
                container.querySelector(".modal-tournament-history-card-tournament-type").src = '../../../assets/icons_128x128/icon_tournament_public.png'
            else
                container.querySelector(".modal-tournament-history-card-tournament-type").src = '../../../assets/icons_128x128/icon_tournament_private.png'

            if (tournamentObject.state === "finished")
                container.querySelector(".modal-tournament-history-card-tournament-date").textContent = this.formatTimestamp(tournamentObject.finishTime);
            else
                container.querySelector(".modal-tournament-history-card-tournament-date").textContent = tournamentObject.state;
            this.domManip.$id("modal-tournament-history-tournament-list-container").appendChild(container);
        }
    },

    hooks: {
        beforeOpen () {
            const currentRoute = $store.fromState("currentRoute");

            if (currentRoute === "profile")
                this.domManip.$id("modal-tournament-history-back-button").style.display = 'none';
            else
                this.domManip.$id("modal-tournament-history-game-history-button").style.display = 'none';

            call(`tournament/history/${$store.fromState("user").id}/`, 'GET').then(data => {
                this.data = data;
                if (!data.tournaments.length) {
                    this.domManip.$id("modal-tournament-history-no-tournaments").style.display = "block";
                    return ;
                }
                this.domManip.$id("modal-tournament-history-no-tournaments").style.display = "none";
                for (let element of data.tournaments)
                    this.createTournamentCard(element);
            })
        },

        afterClose () {
            this.cleanUpTournamentList();
        }
    }
}