import router from "../navigation/router.js";
import $auth from "../auth/authentication.js";
import { $id } from "../abstracts/dollars.js";

export default {
    "authentication-state": async (payload) => {
        if (payload.logout) {
            // don't broadcast logout to other tabs if requested by another tab
            const success = await $auth.logout(false);
            if (success) {
                router("/auth");
            }

            return;
        }

        if (payload.login) {
            // if i am on the auth page, redirect to home
            if ($id('router-view').dataset.view === "auth") {
                $id('navigator').style.display = 'flex'; // show the nav
                router("/home");
            }
        }
    }
}