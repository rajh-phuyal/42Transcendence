import call from '../../abstracts/call.js'
import { $id, $on } from '../../abstracts/dollars.js';
import { populateUserInfo, populateStats, populateProgress, populateButtons } from './script.js';
import { friendshipObjects } from "./objects.js"

export default {
    attributes: {
        
    },

    methods: {

    },

    hooks: {
        beforeRouteEnter() {

        },

        beforeRouteLeave() {

        },

        beforeDomInsertion() {

        },

        afterDomInsertion() {
            call(`user/profile/${this.routeParams.id}/`, "GET").then((res)=>{
                console.log(res);
                populateUserInfo(res);
                populateStats(res);
                populateProgress(res.stats.score.skill, "score-skill-");
                populateProgress(res.stats.score.experience, "score-game-exp-");
                populateProgress(res.stats.score.performance, "score-tournament-exp-");
                populateProgress(res.stats.score.total, "score-total-");
                populateButtons(friendshipObjects[4]);
                
                let element = $id("button-top-right");
                $on(element, "click", friendshipObjects[4].buttonTopRightMethod);
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/