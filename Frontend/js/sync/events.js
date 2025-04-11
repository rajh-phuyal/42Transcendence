import router from "../navigation/router.js";
import { $id } from "../abstracts/dollars.js";
import $store from "../store/store.js";
import $nav from "../abstracts/nav.js";

// @rajh: TODO: this syncer makes issues! With the delay we manage to make it work but the ws conneection is only set in the wrong tab

export default {
    "authentication-state": async (payload) => {
        if (payload.logout) {
            // don't broadcast logout to other tabs if requested by another tab
            // Wait 2 seconds to let the other tabs to logout and then route to auth
            await new Promise(resolve => setTimeout(resolve, 5000));
            router("/logout");
        }

        if (payload.login) {
            // if i am on the auth page, redirect to home
            if ($id('router-view').dataset.view === "auth") {
                await new Promise(resolve => setTimeout(resolve, 5000));
                $store.initializer();

                $nav({ "/profile": { id: $store.fromState("user").id } });

                // show the nav
                $id('navigator').style.display = 'flex';

                router("/home");
            }
        }
    }
}