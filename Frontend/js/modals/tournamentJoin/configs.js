import call from '../../abstracts/call.js'
import router from '../../navigation/router.js';

export default {
    attributes: {
    },

    methods: {
        fetchAvailableTournaments() {
            call('tournament/to-join/', "GET").then(data => {
                const container = this.domManip.$id("modal-tournament-join-list");
                container.innerHTML = "";
                for (let tournament of data.tournaments) {
                    this.createJoinTournamentCard(tournament);
                }
            }).catch((error) => {
                console.warn('API Error:', error);
            });
        },

        createJoinTournamentCard(tournament) {
            let template = this.domManip.$id("modal-tournament-join-card-template").content.cloneNode(true);
            const container = template.querySelector(".modal-tournament-join-card-container");
            container.setAttribute("tournament-id", tournament.id);
            // Set the name
            const nameElement = container.querySelector(".modal-tournament-join-card-tournament-name");
            nameElement.textContent = tournament.name;
            // Set the icon
            const iconElement = container.querySelector(".modal-tournament-join-card-tournament-type");
            if(tournament.public)
                iconElement.src = '../../../assets/icons_128x128/icon_tournament_public.png'
            else
                iconElement.src = '../../../assets/icons_128x128/icon_tournament_private.png'
            const parentContainer = this.domManip.$id("modal-tournament-join-list");
            // Add an event listener to the card
            container.addEventListener("click", this.cardCallback.bind(this));
            // Add the card to the list
            parentContainer.appendChild(template);
        },

        cardCallback(event) {
            const tournamentId = event.currentTarget.getAttribute("tournament-id");
            router('/tournament', { id: tournamentId });
        },
    },

    hooks: {
        beforeOpen () {
            this.fetchAvailableTournaments();
        },

        afterClose () {
        }
    }
}