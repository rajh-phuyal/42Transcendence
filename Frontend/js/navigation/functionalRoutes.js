const functionalRoutes = [
    // template for adding a functional route
    // {
    //     path: "/some-path",
    //     requireAuth: false,
    //     execute: async function () {
    //         console.log("this", this);
    //     },
    // }
    {
        path: "/logout",
        requireAuth: false,
        execute: async function () {
            const success = await this.$auth.logout();
            if (success) {
                this.router("/auth");
            }
        },
    }
];

export { functionalRoutes };