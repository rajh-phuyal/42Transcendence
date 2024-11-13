import { $id } from '../../abstracts/dollars.js';

function populateUserInfo(res) {
    let username = $id("username");   
    username.textContent = "Subject: " + res.username;
    let birthName =$id("birth-name");
    birthName.textContent = "Birth name: " + res.lastName + ", " + res.firstName;
    let lastSeenText =$id("last-seen-text");
    let lastSeenImg =$id("last-seen-image");

    if (res.online)
        lastSeenImg.src = "../../../../assets/onlineIcon.png"; 
    else 
        lastSeenImg.src = "../../../../assets/offlineIcon.png";
    lastSeenText.textContent = "Last seen: " + res.lastLogin;
    let language =$id("language");
    language.textContent = "language: " + res.language;
}

function populateStats(res) {
    let element = $id("stats-games");
    element.textContent = "Games won: " + res.stats.game.won + "/" + res.stats.game.played;
    element = $id("stats-tournament-first-place");
    element.textContent = "1st place in tournament: " + res.stats.tournament.firstPlace + "/" + res.stats.tournament.played;
    element = $id("stats-tournament-second-place");
    element.textContent = "2nd place in tournament: " + res.stats.tournament.secondPlace + "/" + res.stats.tournament.played;
    element = $id("stats-tournament-third-place");
    element.textContent = "3rd place in tournament: " + res.stats.tournament.thirdPlace + "/" + res.stats.tournament.played;
}

function populateProgress(res, identity) {
    let id = identity + "progress";
    let percentageValue = res * 100;

    let progressBar =$id(id);
    progressBar.style.width =  percentageValue + '%';

    id = identity + "percentage";
    let percentage =$id(id);
    percentage.textContent = percentageValue + "%";
}

function populateInfoAndStats(res) {
    populateUserInfo(res);
    populateStats(res);
    populateProgress(res.stats.score.skill, "score-skill-");
    populateProgress(res.stats.score.experience, "score-game-exp-");
    populateProgress(res.stats.score.performance, "score-tournament-exp-");
    populateProgress(res.stats.score.total, "score-total-");
}

export { populateInfoAndStats };