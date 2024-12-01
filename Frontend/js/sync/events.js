import router from "../navigation/router.js";

export default {
    "authentication-state": (payload) => {
        if (payload.logout) {
            console.log("Received logout event from another tab");
            // router("/logout");
        }
    }
}
