import { $id } from '../../abstracts/dollars.js';
import router from '../../navigation/router.js';

export function processIncomingReloadMsg(msg) {
    /* If a client is on the profile of another client who just changes the
    relationship. This will trigger a reload so that the changes are shown
    right away :tada: */
    try {
        const view = $id("router-view");
        const currentProfileId = parseInt(view.getAttribute("data-user-id"));
        if (currentProfileId == msg.userId)
        router("/profile", { id: msg.userId });
    } catch {
        console.warn("Couldn't find the userId attribute in the view -> so no reload of profile. Not a big deal");
        return false;
    }
}
