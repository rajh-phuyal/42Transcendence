import $auth from '../../auth/authentication.js';
import $nav from '../../abstracts/nav.js';
import $store from '../../store/store.js';
import $callToast from '../../abstracts/call.js';
import $syncer from '../../sync/Syncer.js';
import router from '../../navigation/router.js';
import { $id } from '../../abstracts/dollars.js'
import { translate } from '../../locale/locale.js';
import { routes } from '../../navigation/routes.js';

export function initClient(createUser=false, username, password, language) {
    let authAction = ""
    if (createUser)
        authAction = "createUser";
    else
        authAction = "authenticate";
    // Call the auth endpoint via $auth
    $auth?.[authAction](username, password, language)
    .then((response) => {
        // Initialize the store
        $store.initializer();

        // Clear the auth cache from before the authentication
        $auth.clearAuthCache();

        // Set this directly to avoid race condition
        $auth.isAuthenticated = true;

        // Update the store with the new user data
        $store.commit('setIsAuthenticated', true);
        $store.commit('setUser', {
            id: response.userId,
            username: response.username,
            avatar: response.avatar
        });
        // console.error("User logged in / registered. Trying to set local to:", response.locale);
        $store.commit('setLocale', response.locale);
        // Translate all filter inputs // TODO: doesnt work!
        //const filerElements = $class("search-box");
        //console.error("filerElements", filerElements);
        //for (const element of filerElements)
        //    element.setAttribute("placeholder", translate("global:nav", "placeholderSearchbar"));

        // update the profile route params
        $nav({ "/profile": { id: response.userId } });
        $id('nav-avatar').src = `${window.location.origin}/media/avatars/${$store.fromState("user").avatar}`;
        showNav();

        // broadcast login to other tabs
        $syncer.broadcast("authentication-state", { login: true });

        $store.dispatch('loadTranslations', routes.map(route => route.view));
        $store.addMutationListener("setTranslations", (e) => {
            router("/home");
        });
    })
    .catch(error => {
        $callToast("error", error.message);
    });
}

function showNav(){
    let nav = document.getElementById('navigator');
    nav.style.display = 'flex';
    nav.classList.add("d-flex", "flex-row", "justify-content-center");
}
