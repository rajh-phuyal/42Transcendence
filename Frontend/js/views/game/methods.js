import { $id } from '../../abstracts/dollars.js';

export function changeGameState(state) {
    switch (state) {
        case "pending":
            $id("button-quit-game").style.display = "flex";
            return ;
        case "ongoing":
            $id("button-quit-game").style.display = "none";
            return ;
        case "paused":
            $id("button-quit-game").style.display = "none";
            return ;
        case "finished":
            $id("button-quit-game").style.display = "none";
            return ;
    }
    console.warn("FE doen't know what to do with this state:", state);
}