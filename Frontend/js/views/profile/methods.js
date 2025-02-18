import router from '../../navigation/router.js';

export function processIncomingReloadMsg(msg, currentProfile) {
    const currentProfileId = currentProfile.split("-")[1];
    console.warn("Reloading profile current profile: %s, msg: %s", currentProfileId, msg.userId );
    if (currentProfileId == msg.userId)
        router("/profile", { id: msg.userId });
}
