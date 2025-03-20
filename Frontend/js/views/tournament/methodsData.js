import { updateMembers } from "./methodsMembers.js";
import { tournamentData as data } from "./objects.js";

/* This updates the Data of a member. NOT the view! */
export function updateDataMember(member) {
    let found = false;
    for (let i = 0; i < data.tournamentMembers.length; i++) {
        if (data.tournamentMembers[i].id === member.id) {
            // If member exists: update the member data
            data.tournamentMembers[i] = member;
            found = true;
            break;
        }
    }
    if (!found) {
        // If member does not exist: add the member
        data.tournamentMembers.push(member);
    }
}

/* This updates the Data of a game. NOT the view! */
export function updateDataGame(game) {
    let found = false;
    console.log("Updating game data: ", game);
    for (let i = 0; i < data.tournamentGames.length; i++) {
        if (data.tournamentGames[i].id === game.id) {
            // If game exists: update the member data
            data.tournamentGames[i] = game;
            found = true;
            break;
        }
    }
    if (!found) {
        // If game does not exist: add the member
        data.tournamentGames.push(game);
    }
}
