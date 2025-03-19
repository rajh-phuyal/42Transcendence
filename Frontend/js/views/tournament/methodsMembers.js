import { $id , $class} from "../../abstracts/dollars.js";
import { tournamentData } from "./objects.js";
import router from "../../navigation/router.js";


/* This function will fully deal with the participants stored in:
    tournamentData.all.tournamentMembers
*/
export function updateMembers() {
    // Delete all current participants
    $id("container-members-list").querySelectorAll(".tournament-member-card-container").forEach(element => element.remove());
    // Create all participants
    for (let member of tournamentData.all.tournamentMembers)
        createMemberCard(member);
}

function createMemberCard(member) {
    const template = $id("tournament-member-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-member-card-container");
    // Store the user id
    container.setAttribute("userid", member.id)
    // Set the username and avatar
    template.querySelector(".tournament-member-card-username").textContent = member.username;
    template.querySelector(".tournament-member-card-avatar").src = window.origin + "/media/avatars/" + member.avatarUrl;
    // Adjust the styling according to the state
    if (member.state === "pending")
        container.style.filter = "brightness(0.5)";
    else if (member.state === "accepted")
        container.style.filter = "brightness(1)";
    // Add click listener
    container.addEventListener("click", memberCardCallback);
    // Highlight the admin and add the card to the top of the list
    console.warn("member: ", member.role);
    if (member.id === tournamentData.all.tournamentInfo.adminId) {
        container.style.border = "3px solid black";
        template.querySelector(".tournament-member-card-username").textContent += " (admin)"; // TODO: translate
        $id("container-members-list").prepend(container);
    } else
        $id("container-members-list").appendChild(container);

    console.log("member: added: ", member.username);
}

function memberCardCallback(event) {
    const userId = event.currentTarget.getAttribute("userid");
    router(`/profile`, { id: userId });
}