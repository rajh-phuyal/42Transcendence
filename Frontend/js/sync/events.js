import router from "../navigation/router.js";
import $auth from "../auth/authentication.js";
import { $id } from "../abstracts/dollars.js";
import $store from "../store/store.js";
import $nav from "../abstracts/nav.js";
import { routes } from "../navigation/routes.js";

export default {
    "authentication-state": async (payload) => {
        if (payload.logout) {
            // don't broadcast logout to other tabs if requested by another tab
            const success = await $auth.logout(false);
            if (success) {
                // remove this to load the translations again
				$store.removeMutationListener("setTranslations");

                // load the translations again
                $store.dispatch('loadTranslations', routes.map(route => route.view));
				const nav = $id("navigator");
				nav.classList.remove("d-flex", "flex-row", "justify-content-center");
				nav.style.display = 'none';
				$store.addMutationListener("setTranslations", (e) => {
					// console.log("mutation state", e);
					router("/auth");
				});
            }

            return;
        }

        if (payload.login) {
            // if i am on the auth page, redirect to home
            if ($id('router-view').dataset.view === "auth") {
                $store.initializer();

                $nav({ "/profile": { id: $store.fromState("user").id } });

                // show the nav
                $id('navigator').style.display = 'flex';

                router("/home");
            }
        }
    }
}