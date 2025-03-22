import { $id } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import $store from '../../store/store.js';

function populateUserInfo(res) {
    let username = $id("username");
    username.innerHTML = `${translate("profile", "subject")}${res.username}`;
    const element = $id("avatar");
    element.src = window.origin + '/media/avatars/' + res.avatar;
    let birthName =$id("birth-name");
    birthName.innerHTML = `<b>${translate("profile", "birthName")}</b>${res.lastName}, ${res.firstName}`;
    let lastSeenText =$id("last-seen-text");
    let lastSeenImg =$id("last-seen-image");

    if (res.online)
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_online.png";
    else
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_offline.png";
    lastSeenText.innerHTML =`<b>${translate("profile", "lastSeen")}</b>${res.lastLoginFormatted}`;
    let language =$id("language");
    language.innerHTML = `<b>${translate("profile", "language")}</b>${res.language}`;
}

function populateStats(res) {
    let element = $id("stats-games");
    element.innerHTML = `${translate("profile", "gamesWon")}${res.stats.game.won}/${res.stats.game.played}`;
    element = $id("stats-tournament-first-place");
    element.innerHTML = `${translate("profile", "firstPlace")}${res.stats.tournament.firstPlace}/${res.stats.tournament.played}`;
    element = $id("stats-tournament-second-place");
    element.innerHTML = `${translate("profile", "secondPlace")}${res.stats.tournament.secondPlace}/${res.stats.tournament.played}`;
    element = $id("stats-tournament-third-place");
    element.innerHTML = `${translate("profile", "thirdPlace")}${res.stats.tournament.thirdPlace}/${res.stats.tournament.played}`;
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