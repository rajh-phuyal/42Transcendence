const routes = [
    {
        path: "/",
        view: "home",
        requireAuth: true
    },
    {
        path: "/home",
        view: "home",
        requireAuth: true,
        modals: ["createGame", "tournament"]
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
        modals: ["template", "editProfile", "createGame", "editFriendship", "newConversation", "friendList"]
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
    { // TODO: @rajh: not sure if I should add 404 here but without the translation wasn't working
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