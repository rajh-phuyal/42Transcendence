import { $id } from '../../abstracts/dollars.js';
import { translate } from '../../locale/locale.js';
import { loadTimestamp } from '../../abstracts/timestamps.js';

function populateUserInfo(res) {
    // Set the username
    let username = $id("username");
    username.innerHTML = `${translate("profile", "subject")}${res.username}`;
    // Set the online eye icon
    let lastSeenImg =$id("last-seen-image");
    if (res.online)
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_online.png";
    else
        lastSeenImg.src = "../../../../assets/icons_128x128/icon_offline.png";
    // Set the avatar
    const element = $id("avatar");
    element.src = window.origin + '/media/avatars/' + res.avatar;
    // Set the birth name
    let birthName =$id("birth-name");
    let fullName = ""
    if (res.firstName)
        fullName = res.firstName + ", ";
    fullName += res.lastName;
    console.error(fullName);
    if(fullName == "")
        fullName = "&nbsp;";
    birthName.innerHTML = `<b>${translate("profile", "birthName")}</b>${fullName}`;
    // Set the last seen text
    let lastSeenTextElement = $id("last-seen-text");
    let lastSeenText = "";
    if (res.lastLogin) {
        res.lastLogin = loadTimestamp(res.lastLogin, "YYYY-MM-DD HH:mm"); // Convert lastLogin to local time using moment.js
        lastSeenText = `<b>${translate("profile", "lastSeen")}</b>${res.lastLogin}`;
    } else
    lastSeenText = `<b>${translate("profile", "lastSeen")}</b>&nbsp;`;
    lastSeenTextElement.innerHTML = lastSeenText;
    // Set the language
    let language = $id("language");
    if (res.language)
        language.innerHTML = `<b>${translate("profile", "language")}</b>${res.language}`;
    else
        language.innerHTML = `<b>${translate("profile", "language")}</b>&nbsp;`;
    let notes = $id("notes");
    if (res.notes !== "")
        notes.innerHTML = `<b>${translate("profile", "notes")}</b>${res.notes}`;
}

function allignStats(elementId, a, b){
    const offset = 6;
    let element = $id(elementId);
    if(!element)
        return
    // Count the chars of a, add spacs until offset is reached, add b
    element.innerHTML = (a + "&nbsp;".repeat(offset - a.length) + b);
}

function populateStats(res) {
    if (res.stats === "")
        return ;
    allignStats("stats-games",                  `${res.stats.game.won}/${res.stats.game.played}`,                           translate("profile", "gamesWon"));
    allignStats("stats-tournament-first-place", `${res.stats.tournament.firstPlace}/${res.stats.tournament.played}`,        translate("profile", "firstPlace"));
    allignStats("stats-tournament-second-place",`${res.stats.tournament.secondPlace}/${res.stats.tournament.played}`,       translate("profile", "secondPlace"));
    allignStats("stats-tournament-third-place", `${res.stats.tournament.thirdPlace}/${res.stats.tournament.played}`,        translate("profile", "thirdPlace"));
}

function populateProgress(res, identity) {
    let percentageValue = res;
    let progressBar = $id(identity);
    progressBar.style.width =  percentageValue + '%';
    progressBar.setAttribute("aria-valuenow", percentageValue);
}

function populateInfoAndStats(res) {
    populateUserInfo(res);
    populateStats(res);
    if (res.stats === "")
        return ;
    populateProgress(res.stats.score.skill,         "score-skill-progress");
    populateProgress(res.stats.score.experience,    "score-game-exp-progress");
    populateProgress(res.stats.score.performance,   "score-tournament-exp-progress");
    populateProgress(res.stats.score.total,         "score-total-progress");
}

export { populateInfoAndStats };