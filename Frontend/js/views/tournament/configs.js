import call from '../../abstracts/call.js'

export default {
    attributes: {

    },

    methods: {

        createParticipantCard(userData) {

            //console.log("helo", userData);
            let card = this.domManip.$id("tournament-list-card-template").content.cloneNode(true);
            // atripute grey background color if the user is not in the tournament yet
            if (userData.userState == "pending")
                card.querySelector(".card").style.backgroundColor = "grey";

            card.querySelector(".username").textContent = userData.username;
            //console.log("card:", card);
            return card;
        },

        buildParticipantsList(list) {
            //console.log("Building participants list from list: ", list);
            const mainDiv = this.domManip.$id("tournament-list");
            for (let element of list){
                //console.log("participant card:", particpantCard);
                mainDiv.appendChild(this.createParticipantCard(element));
            }
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
            const id = 4;
            call(`tournament/lobby/${id}/`, 'GET').then(data => {
                //console.log(data);
                let stateColor;
                if (data.tournamentState == "setup")
                    stateColor = "orange";
                else if (data.tournamentState == "ongoing")
                    stateColor = "green";
                else
                    stateColor = "red";
                this.domManip.$id("status").style.backgroundColor = stateColor;
                this.domManip.$id("tournament-name").textContent = data.tournamentName;

                this.buildParticipantsList(data.tournamentMembers);

            })
        },
    }
}