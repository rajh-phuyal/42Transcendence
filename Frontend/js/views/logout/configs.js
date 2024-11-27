import { $id } from "../../abstracts/dollars.js"; //TODO: replace by binder.domManip
import $callToast from "../../abstracts/callToast.js";

export default {
    attributes: {
        intervalId: undefined
    },

    methods: {
        redirectToLogin() {
            // show the navigation bar
            const navBar = $id('navigator');
            navBar.style.display = 'block';

            clearInterval(this.intervalId);
            this.router('/auth');
        }
    },

    hooks: {
        beforeDomInsertion() {
            // hide the navigation bar
            const navBar = $id('navigator');
            navBar.style.display = 'none';

            // clear the interval
            if (this.intervalId) clearInterval(this.intervalId);
        },

        afterDomInsertion() {
            this.$auth.logout();

            $callToast("success", 'We would say "see you soon" but we are always watching...');

            // do a countdown to redirect
            const countdown = $id('login-redirect-countdown');

            countdown.textContent = `${2}s`;

            this.intervalId = setInterval(() => {
                const current = _.parseInt(countdown.textContent);

                countdown.textContent = `${current - 1}s`;

                if (!current) this.redirectToLogin();
            }, 1000);
        },
    }
};