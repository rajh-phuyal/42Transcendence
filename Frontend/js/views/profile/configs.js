import call from '../../abstracts/call.js'
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
                
                // let skillProgressBar =$id("progress");
                // let skillPercentageValue = res.stats.score.skill * 100;
                // skillProgressBar.style.width =  skillPercentageValue + '%';
                // let skillPercentage =$id("score-skill-percentage");
                // skillPercentage.textContent = skillPercentageValue + "%";
            })
            // on error?
        },
    }
}

/*
        2024.02.02  06:30h
        Under Surveillance
*/