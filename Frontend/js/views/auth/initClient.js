import $auth from '../../auth/authentication.js';
import $nav, { setNavVisibility } from '../../abstracts/nav.js';
import $store from '../../store/store.js';
import { $id } from '../../abstracts/dollars.js'

export async function initClient(createUser=false, username, password, language) {
    let authAction = ""
    if (createUser)
        authAction = "createUser";
    else
        authAction = "authenticate";
    // Call the auth endpoint via $auth
    let response;
    try {
        response = await $auth?.[authAction](username, password, language)
    } catch (error) {
        return ;
    }
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

    // update the profile route params
    $nav({ "/profile": { id: response.userId } });
    $id('nav-avatar').src = `${window.location.origin}/media/avatars/${$store.fromState("user").avatar}`;
    setNavVisibility(true);

    // broadcast login to other tabs
    //$syncer.broadcast("authentication-state", { login: true });
}
