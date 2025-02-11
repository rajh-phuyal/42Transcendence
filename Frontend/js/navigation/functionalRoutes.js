import { $id } from '../abstracts/dollars.js';
import { routes } from "../navigation/routes.js";

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
                // remove this to load the translations again
                this.$store.removeMutationListener("setTranslations");

                // load the translations again
                this.$store.dispatch('loadTranslations', routes.map(route => route.view));
				const nav = $id("navigator");
				nav.classList.remove("d-flex", "flex-row", "justify-content-center");
				nav.style.display = 'none';
                this.router("/auth");
            }
        },
    }
];

export { functionalRoutes };