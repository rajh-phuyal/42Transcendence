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
    { // TODO: @rajh: not sure if I should add 404 here but without the translation wasn't working
        path: "/404",
        view: "404",
        requireAuth: false,
    },
];

export { routes };