import { openConversation } from "./methods.js"

export const buttonObjects = [
    // send message button
    {
        imageMessage: "../../../../assets/profileView/sendMessageIcon.png",
        imageMessageUnseen: "",
        method: undefined
    },
    // logout button
    {
        image: "",
        method: undefined
    },
    // edit button
    {
        image: "",
        method: undefined
    },
    // invite to play
    {
        image: "",
        method: undefined
    },

    // player views his own profile
    {
        buttonTopLeftImagePath: undefined,
        buttonTopLeftMethod: undefined,
        buttonTopMiddleImagePath: "",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "",
        buttonTopRightMethod: "",
        buttonTopRightSecondImagePath: undefined,
    },
    // player is not cool with user
    {
        buttonTopLeftImagePath: undefined,
        buttonTopLeftMethod: undefined,
        buttonTopMiddleImagePath: "",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "",
        buttonTopRightMethod: "",
        buttonTopRightSecondImagePath: "",
    },
    // friend request received but not accepted
    {
        buttonTopLeftImagePath: undefined,
        buttonTopLeftMethod: undefined,
        buttonTopMiddleImagePath: "",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "",
        buttonTopRightMethod: "",
        buttonTopRightSecondImagePath: "",
    },
    // friend request sent but not accepted
    {
        buttonTopLeftImagePath: undefined,
        buttonTopLeftMethod: undefined,
        buttonTopMiddleImagePath: "",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "",
        buttonTopRightMethod: "",
        buttonTopRightSecondImagePath: "",
    },
    // users are friends
    {
        buttonTopLeftImagePath: "../../../../assets/profileView/friendsIcon.png",
        buttonTopLeftMethod: "",
        buttonTopMiddleImagePath: "../../../../assets/profileView/invitePongIcon.png",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "../../../../assets/profileView/sendMessageIcon.png",
        buttonTopRightMethod: openConversation,
        buttonTopRightSecondImagePath: "",
    },
    // profile of a user that is blocked
    {
        buttonTopLeftImagePath: undefined,
        buttonTopLeftMethod: undefined,
        buttonTopMiddleImagePath: "",
        buttonTopMiddleMethod: "",
        buttonTopRightImagePath: "",
        buttonTopRightMethod: "",       // remove block
        buttonTopRightSecondImagePath: "",
    },
]