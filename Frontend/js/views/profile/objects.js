export const buttonObjects = [
    // users are friends 0
    {
        text: "Do you want to remove this user form your friends list?",
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/", 
        action: "remove",
    },
    // users are not friends 1
    {
        text: "Do you want to send this user a friend request?",
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/",
        action: "send",
    },
    // friend request received 2
    {
        text: "Do you want accept this user's friend request?",
        secundaryButton: true,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "PUT",
        Url: "user/relationship/",
        action: "accept",
        // DELETE cancel
    },
    // friend request sent 3
    {
        text: "Do you want to cancel your friend request?",
        secundaryButton: false,
        leftButtonMethod: undefined,
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/",
        action: "cancel",
    },
    // block user 4
    {
        text: "Do you want to block this user?",
        leftButtonMethod: undefined,
        method: "POST",
        Url: "user/relationship/",
        action: "block",
    },
    // unblock user 5
    {
        text: "Do you want to unblock this user?",
        leftButtonMethod: undefined,
        method: "DELETE",
        Url: "user/relationship/",
        action: "unblock",
    }
]