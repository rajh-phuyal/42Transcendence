const routes = [
    {
        path: "/",
        view: "home",
        requireAuth: true,
        modals: ["createGame" , "tournamentMain", "tournamentCreate", "tournamentJoin", "tournamentHistory"]
    },
    {
        path: "/home",
        view: "home",
        requireAuth: true,
        modals: ["createGame" , "tournamentMain", "tournamentCreate", "tournamentJoin", "tournamentHistory"]
    },
    {
        path: "/game",
        view: "game",
        requireAuth: true
    },
    {
        path: "/tournament",
        view: "tournament",
        requireAuth: true
    },
    {
        path: "/profile",
        view: "profile",
        requireAuth: true,
        modals: ["editProfile", "createGame", "editFriendship", "newConversation", "friendsList", "gameHistory"]
    },
    {
        path: "/chat",
        view: "chat",
        requireAuth: true,
        modals: ["createGame"]
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
    },
	{
		path: "/barely-responsive",
		view: "barely-responsive",
		requireAuth: false,
	}
];

export { routes };