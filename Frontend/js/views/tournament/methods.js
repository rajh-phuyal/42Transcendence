createParticipantCard(userData) {

    //console.log("helo", userData);
    let card = this.domManip.$id("tournament-list-card-template").content.cloneNode(true);
    // atripute grey background color if the user is not in the tournament yet
    if (userData.userState == "pending")
        card.querySelector(".card").style.backgroundColor = "grey";

    card.querySelector(".username").textContent = userData.username;
    //console.log("card:", card);
    return card;
}