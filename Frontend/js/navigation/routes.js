const routes = [
    {
        path: "/",
        view: "home",
        requireAuth: true
    },
    {
        path: "/home",
        view: "home",
        requireAuth: true
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
        requireAuth: true
    },
    {
        path: "/chat",
        view: "chat",
        requireAuth: true
    },
    {
        path: "/auth",
        view: "auth",
        requireAuth: false,
    },
];

export { routes };