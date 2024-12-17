import call from '../../abstracts/call.js'

export default {
    attributes: {

    },

    methods: {

        createParticipantCard(userData) {

            let card = this.domManip.$id("tournament-list-card-template").content.cloneNode(true);

            // atripute grey background color if the user is not in the tournament yet
            card.querySelector(".card").style.backgroundColor = "grey";
            card.querySelector(".username").textContent = userData.username;

        },

        
        buildParticipantsList(list) {
            const mainDiv = this.domManip.$id("tournament-list");

            for (element of list) 
                mainDiv.appendChild(createParticipantCard(element));
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
            const id = 1;
            call(`tournament/lobby/${id}/`, 'GET').then(data => {

                let stateColor;
                if (data.tournament.state == "setup")
                    stateColor = "red";
                else
                    stateColor = "green";

                this.domManip.$id("status").style.backgroundColor = stateColor;
                this.domManip.$id("tournament-name").textContent = data.tournamentName;
                
                
            })
        },
    }
}