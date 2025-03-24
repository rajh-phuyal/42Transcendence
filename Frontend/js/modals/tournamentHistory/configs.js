import $store from '../../store/store.js'
import call from '../../abstracts/call.js'
import { loadTimestamp } from '../../abstracts/timestamps.js';
import router from '../../navigation/router.js';
import { translate } from '../../locale/locale.js';

export default {
    attributes: {
        tournaments:[],
    },

    methods: {
        translateElements() {
            this.domManip.$id("modal-tournament-history-search-bar").placeholder = translate("tournamentHistory", "placeholderFilter");
        },

        formatTimestamp(isoTimestamp) {
            return loadTimestamp(isoTimestamp, "YY-MM-DD hh:mm");
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

        searchBarTypeListener(event) {
            const searchBarElement = this.domManip.$id("modal-tournament-history-search-bar");
            let inputValue = searchBarElement.value.trim();

            const tournamentElements = this.domManip.$class("modal-tournament-history-card");
            for (let element of tournamentElements) {
                element.style.display = "none";
            }
            this.domManip.$id("modal-tournament-list-list-result-not-found-message").style.display = "none";

            const filteredArray =  this.tournaments.filter(value => value.startsWith(inputValue));
            if (!filteredArray.length)
                this.domManip.$id("modal-tournament-list-list-result-not-found-message").style.display = 'flex';

            for (let name of filteredArray) {
                const elementsToFilter = this.domManip.$class(`t-${name}`)
                for (let element of elementsToFilter)
                    element.style.display = 'grid';
            }
        },

        createTournamentCard(tournamentObject) {
            const template = this.domManip.$id("modal-tournament-history-card-template").content.cloneNode(true);
            const container = template.querySelector(".modal-tournament-history-card");

            if (!this.tournaments.includes(tournamentObject.name))
                this.tournaments.push(tournamentObject.name);
            container.setAttribute("tournament-id", tournamentObject.id);
            this.domManip.$addClass(container, `t-${tournamentObject.name}`);
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
                this.translateElements();
                if (!data.tournaments.length) {
                    this.domManip.$id("modal-tournament-history-no-tournaments").style.display = "block";
                    return ;
                }
                this.domManip.$id("modal-tournament-history-no-tournaments").style.display = "none";
                for (let element of data.tournaments)
                    this.createTournamentCard(element);
                this.domManip.$on(this.domManip.$id("modal-tournament-history-search-bar"), "input", this.searchBarTypeListener);
            })
        },

        afterClose () {
            this.cleanUpTournamentList();
            this.domManip.$off(this.domManip.$id("modal-tournament-history-search-bar"), "input", this.searchBarTypeListener);
        }
    }
}