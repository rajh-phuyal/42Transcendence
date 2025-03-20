const routes = [
    {
        path: "/",
        view: "home",
        requireAuth: true,
        modals: ["createGame" , "tournamentMain", "tournamentCreate", "tournamentJoin", "tournamentHistory"],
    },
    {
        path: "/home",
        view: "home",
        requireAuth: true,
        modals: ["createGame" , "tournamentMain", "tournamentCreate", "tournamentJoin", "tournamentHistory"],
    },
    {
        path: "/game",
        view: "game",
        requireAuth: true,
        backgroundColor: "black",
    },
    {
        path: "/tournament",
        view: "tournament",
        requireAuth: true,
        backgroundColor: "black",
    },
    {
        path: "/profile",
        view: "profile",
        requireAuth: true,
        modals: ["editProfile", "createGame", "editFriendship", "newConversation", "friendsList", "gameHistory", "avatarCropper", "tournamentHistory"],
        backgroundColor: "black", // TODO: i guess blach here doesnt look nice
    },
    {
        path: "/chat",
        view: "chat",
        requireAuth: true,
        modals: ["createGame"],
    },
    {
        path: "/auth",
        view: "auth",
        requireAuth: false,
    },
    {
        path: "/404",
        view: "404",
        requireAuth: false,
        backgroundColor: "black",
    },
	{
		path: "/barely-responsive",
		view: "barely-responsive",
		requireAuth: false,
	}
];

export { routes };