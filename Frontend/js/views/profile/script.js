import { $id } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import $store from '../../store/store.js';

function populateUserInfo(res) {
    let username = $id("username");
    username.textContent = translate("profile", "subject") + res.username;
    const element = $id("avatar");
    element.src = window.origin + '/media/avatars/' + res.avatarUrl;
    let birthName =$id("birth-name");
    birthName.textContent = translate("profile", "birthName") + res.lastName + ", " + res.firstName;
    let lastSeenText =$id("last-seen-text");
    let lastSeenImg =$id("last-seen-image");

    if (res.online)
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_online.png";
    else
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_offline.png";
    lastSeenText.textContent = translate("profile", "lastSeen") + res.lastLogin;
    let language =$id("language");
    language.textContent = translate("profile", "language") + res.language;
}

function populateStats(res) {
    let element = $id("stats-games");
    element.textContent = translate("profile", "gamesWon") + res.stats.game.won + "/" + res.stats.game.played;
    element = $id("stats-tournament-first-place");
    element.textContent = translate("profile", "firstPlace") + res.stats.tournament.firstPlace + "/" + res.stats.tournament.played;
    element = $id("stats-tournament-second-place");
    element.textContent = translate("profile", "secondPlace") + res.stats.tournament.secondPlace + "/" + res.stats.tournament.played;
    element = $id("stats-tournament-third-place");
    element.textContent = translate("profile", "thirdPlace") + res.stats.tournament.thirdPlace + "/" + res.stats.tournament.played;
}

function populateProgress(res, identity) {
    let id = identity + "progress";
    let percentageValue = res;

    let progressBar =$id(id);
    progressBar.style.width =  percentageValue + '%';

    // TODO: check if still needed
    //id = identity + "percentage";
    //let percentage =$id(id);
    //percentage.textContent = percentageValue + "%";
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