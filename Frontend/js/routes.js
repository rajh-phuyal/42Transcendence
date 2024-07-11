const routes = [
    {
        path: "/",
        view: "home.html",
        requireAuth: true
    },
    {
        path: "/home",
        view: "home.html",
        requireAuth: true
    },
    {
        path: "/battle",
        view: "battle.html",
        requireAuth: true
    },
    {
        path: "/tornament",
        view: "battle.html",
        requireAuth: true
    },
    {
        path: "/profile",
        view: "profile.html",
        requireAuth: true
    },
    {
        path: "/chat",
        view: "chat.html",
        requireAuth: true
    },
    {
        path: "/auth",
        view: "auth.html",
        requireAuth: false,
    },
];

export { routes };