import { translate } from '../../locale/locale.js';

export const buttonObjects = {
    // users are friends 0
    "friend": {
        text: translate("profile", "confirmRemoveFriend"),
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/remove/",
    },
    // users are not friends 1
    "noFriend": {
        text: translate("profile", "sendRequest"),
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/send/",
    },
    // friend request received 2
    "requestReceived": {
        text: translate("profile", "acceptRequest"),
        secondaryButton: true,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "PUT",
        Url: "user/relationship/accept/",
    },
    // friend request sent 3
    "requestSent": {
        text: translate("profile", "cancelRequest"),
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/cancel/",
    },
    // block user 4
    "unblocked": {
        text: translate("profile", "blockUser"),
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/block/",
    },
    // unblock user 5
    "blocked": {
        text: translate("profile", "unblockUser"),
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/unblock/",
    }
}