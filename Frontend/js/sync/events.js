import router from "../navigation/router.js";
import { $id } from "../abstracts/dollars.js";
import $store from "../store/store.js";
import $nav from "../abstracts/nav.js";

export default {
    "authentication-state": async (payload) => {
        if (payload.logout) {
            // don't broadcast logout to other tabs if requested by another tab
            router("/logout");
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