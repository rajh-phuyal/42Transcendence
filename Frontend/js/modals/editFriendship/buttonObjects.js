export const buttonObjects = {
    // users are friends 0
    "friend": {
        textKey: "confirmRemoveFriend",
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/remove/",
    },
    // users are not friends 1
    "noFriend": {
        textKey: "sendRequest",
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/send/",
    },
    // friend request received 2
    "requestReceived": {
        textKey: "acceptRequest",
        secondaryButton: true,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "PUT",
        Url: "user/relationship/accept/",
    },
    // friend request sent 3
    "requestSent": {
        textKey: "cancelRequest",
        secondaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/cancel/",
    },
    // block user 4
    "unblocked": {
        textKey: "blockUser",
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/block/",
    },
    // unblock user 5
    "blocked": {
        text: "unblockUser",
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/unblock/",
    }
}