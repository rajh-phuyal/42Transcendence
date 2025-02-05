import { translate } from '../../locale/locale.js';

export const buttonObjects = {
    // users are friends 0
    "friend": {
        text: translate("profile", "confirmRemoveFriend"),
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/",
        action: "remove",
    },
    // users are not friends 1
    "noFriend": {
        text: translate("profile", "sendRequest"),
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/",
        action: "send",
    },
    // friend request received 2
    "requestReceived": {
        text: translate("profile", "acceptRequest"),
        secundaryButton: true,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "PUT",
        Url: "user/relationship/",
        action: "accept",
        // DELETE cancel
    },
    // friend request sent 3
    "requestSent": {
        text: translate("profile", "cancelRequest"),
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/",
        action: "cancel",
    },
    // block user 4
    "unblocked": {
        text: translate("profile", "blockUser"),
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/",
        action: "block",
    },
    // unblock user 5
    "blocked": {
        text: translate("profile", "unblockUser"),
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/",
        action: "unblock",
    }
}