// TODO: I guess we can delete this file?

import router from '../../navigation/router.js';
import { processIncomingWsChatMessage } from '../chat/methods.js';

function openConversation() {
    router("/chat");
}

export function processIncomingReloadMsg(msg, currentProfile) {
    const currentProfileId = currentProfile.split("-")[1];
    console.warn("Reloading profile current profile: %s, msg: %s", currentProfileId, msg.userId );
    if (currentProfileId == msg.userId)
        router("/profile", { id: msg.userId });
}

export { openConversation };