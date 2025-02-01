import { $id } from '../../abstracts/dollars.js';

export function changeGameState(state) {
    switch (state) {
        case "ongoing": // transition lobby to game
            $id("button-quit-game").style.display = "none";
            return ;
        case "paused": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            return ;
        case "finished": // transition game to lobby
            $id("button-quit-game").style.display = "none";
            return ;
    }
    console.warn("FE doen't know what to do with this state:", state);
}

export function updateReadyState(readyStateObject) {

    if (readyStateObject.playerLeft) {
        $id("player-left-state-spinner").style.display = "none";
        $id("player-left-state").innerText = translate("game", "ready");
    }
    else {
        $id("player-left-state-spinner").style.display = "block";
        $id("player-left-state").innerText = "";
    }

    if (readyStateObject.playerRight) {
        $id("player-right-state-spinner").style.display = "none";
        $id("player-right-state").innerText = translate("game", "ready");
    }
    else {
        $id("player-right-state-spinner").style.display = "block";
        $id("player-right-state").innerText = "";
    }

    if (readyStateObject.startTime)
        console.warn("Start Time:", readyStateObject.startTime);
}