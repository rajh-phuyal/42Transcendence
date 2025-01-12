import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id, $on, $off } from './dollars.js';

function updateUserInfo() {
    $id('profile-nav-avatar').src = `${window.location.origin}/media/avatars/${$store.fromState("user").avatar}`;
}

const styleUpdateMap = {
    '/profile': updateUserInfo
}

// navigation bar helpers
function updateRouteParams(navigationPathParams, navigationBarMap) {
    for (const [path, params] of Object.entries(navigationPathParams)) {
        let route = navigationBarMap.find(route => route.path === path);
        if (!route) continue;

        let navbarObject = $id(route?.id);
        if (!navbarObject) continue;

        styleUpdateMap?.[route.path]?.();

        // Remove old handler if it exists
        if (navbarObject._clickHandler) {
            $off(navbarObject, 'click', navbarObject._clickHandler);
        }

        // Create and store new handler
        navbarObject._clickHandler = () => router(route.path, params);
        $on(navbarObject, 'click', navbarObject._clickHandler);
    }
}

/**
 * @param {Object} navigationPathParams - an object that contains the path and the new params
 * @example {
 *     path: "/some-path",
 *     params: {
 *         id: 1
 *     }
 * }
 */
export default function $nav(navigationPathParams = null) {
    console.log("Navigattion :", navigationPathParams, $store.fromState("user"));
    // nav bar route to Dom elements map
    const navigationBarMap = [
        { id: 'home-nav', path: '/home' },
        { id: 'game-nav', path: '/game' },
        { id: 'tournament-nav', path: '/tournament' },
        { id: 'chat-nav', path: '/chat' },
        { id: 'logout-nav', path: '/logout' },
        { id: 'profile-nav-avatar', path: '/profile' },
        { id: 'login-nav', path: '/auth' },
        { id: 'register-nav', path: '/auth' }
    ];

    // only update the route params if the navigationPathParams is provided
    if (navigationPathParams) {
        updateRouteParams(navigationPathParams, navigationBarMap);
        return;
    }

    // routes with params
    const routeFinder = (path) => navigationBarMap.find(route => route.path === path);

    routeFinder('/profile').params = { id: $store.fromState("user").id };
    routeFinder('/chat').params = { id: undefined };

    // additional data and styles
    styleUpdateMap?.[routeFinder('/profile').path]?.();

    // Initial setup of handlers
    for (const route of navigationBarMap) {
        const navbarObject = $id(route.id);
        if (!navbarObject) continue;

        navbarObject._clickHandler = () => router(route.path, route?.params);
        $on(navbarObject, 'click', navbarObject._clickHandler);
    }
}
