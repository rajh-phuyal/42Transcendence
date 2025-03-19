import { updateMembers } from "./methodsMembers.js";
import { tournamentData } from "./objects.js";

/* This updates the Data of a member and than triggers the updateMembers funciton */
export function updateDataMembers(member) {
    console.error("member:", member);

    updateMembers();
}