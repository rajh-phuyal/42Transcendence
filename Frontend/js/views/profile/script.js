import { $id } from '../../abstracts/dollars.js';

function populateUserInfo(res) {
    let username = $id("username");   
    username.textContent = "Subject: " + res.username;
    let birthName =$id("birth-name");
    birthName.textContent = "Birth name: " + res.lastName + ", " + res.firstName;
    let lastSeenText =$id("last-seen-text");
    let lastSeenImg =$id("last-seen-image");

    if (res.online) {
        lastSeenText.textContent = "Last seen: " + res.lastLogin;
        lastSeenImg.src = "../../../../assets/onlineIcon.png";
    }
    else {
        lastSeenText.textContent = "Last seen: Under surveillance";
        lastSeenImg.src = "../../../../assets/offlineIcon.png";
    }
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

// function populateButtons(object) {
//     console.log("object");
//     console.log(object);
//     let element = $id("button-top-left");
//     element.src = object.buttonTopLeftImagePath;
//     element = $id("button-top-middle");
//     element.src = object.buttonTopMiddleImagePath;
//     element = $id("button-top-right");
//     element.src = object.buttonTopRightImagePath;
//     element = $id("button-bottom-left");
//     element.src = "../../../../assets/profileView/gamingHistoryIcon.png";
//     element = $id("button-bottom-right");
//     element.src = "../../../../assets/profileView/FriendsListIcon.png";
// }

function populateInfoAndStats(res) {
    populateUserInfo(res);
    populateStats(res);
    populateProgress(res.stats.score.skill, "score-skill-");
    populateProgress(res.stats.score.experience, "score-game-exp-");
    populateProgress(res.stats.score.performance, "score-tournament-exp-");
    populateProgress(res.stats.score.total, "score-total-");
}

export { populateInfoAndStats };