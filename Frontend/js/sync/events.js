import router from "../navigation/router.js";
import $auth from "../auth/authentication.js";
import $store from "../store/store.js";

export default {
    "authentication-state": (payload) => {
        if (payload.logout) {
            console.log("Authentication state", payload);
            $auth.logout();
            router("/auth");
        }
    },
    "local-state": (payload) => {
        $store.state = { ...$store.state, ...payload };
    }
}
