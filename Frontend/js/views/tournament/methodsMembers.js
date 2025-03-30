import router from "../../navigation/router.js";
import { $id } from "../../abstracts/dollars.js";
import { translate } from '../../locale/locale.js';
import { tournamentData as data } from "./objects.js";

/* This function will fully deal with the participants stored in:
    tournamentData.all.tournamentMembers
*/
export function updateMembers() {
    // Create all participants
    for (let member of data.tournamentMembers) {
        // Find member card
        let container = $id("container-members-list").querySelector(`[userid="${member.id}"]`);
        // If the member card doesn't exist, create it
        if(!container)
            container = createTemplateMemberCard(member);
        // Update the member card
        updateMemberCard(container, member);
    }
}

/* This will create the html node */
function createTemplateMemberCard(member) {
    const template = $id("tournament-member-card-template").content.cloneNode(true);
    const container = template.querySelector(".tournament-member-card-container");
    // Store the user id
    container.setAttribute("userid", member.id)
    // Add click listener
    container.addEventListener("click", memberCardCallback);
    // Set username and avatar
    container.querySelector(".tournament-member-card-username").textContent += member.username; // += to not overwrite the admin tag
    container.querySelector(".tournament-member-card-avatar").src = window.origin + "/media/avatars/" + member.avatar;
    // Highlight the admin
    if (member.id === data.tournamentInfo.adminId) {
        container.style.border = "3px solid black";
        container.querySelector(".tournament-member-admin-icon").style.display = "block";
        container.querySelector(".tournament-member-admin-icon").style.height = "90%";
        container.querySelector(".tournament-member-admin-icon").title = translate("tournament", "tooltipTournamentAdmin");
    }
    // Append the container
    $id("container-members-list").appendChild(container);
    return container;
}

function updateMemberCard(container, member) {
    // Adjust the styling according to the state
    if (member.state === "pending")
        container.style.filter = "brightness(0.5)";
    else if (member.state === "accepted")
        container.style.filter = "brightness(1)";
    else if (member.state === "left")
        container.remove();
}

function memberCardCallback(event) {
    const userId = event.currentTarget.getAttribute("userid");
    router(`/profile`, { id: userId });
}