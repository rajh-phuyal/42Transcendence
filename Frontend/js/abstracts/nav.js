import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id } from './dollars.js';

// navigation bar helpers
function updateRouteParams(navigationPathParams, navigationBarMap) {
    for (const [path, params] of Object.entries(navigationPathParams)) {
        let route = navigationBarMap.find(route => route.path === path);
        if (!route) continue;

        let navbarObject = $id(route?.id);
        if (!navbarObject) continue;

        // remove old handeler
        navbarObject?.removeEventListener('click', () => router(route.path, route?.params));

        // update the route params
        route.params = params;

        // add the new handler
        navbarObject?.addEventListener('click', () => router(route.path, params));
    }
}

function setUpDataAndStyles() {
    $id('profile-nav-username').textContent = $store.fromState("user").username;
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
    // nav bar route to Dom elements map
    const navigationBarMap = [
        { id: 'home-nav', path: '/home' },
        { id: 'game-nav', path: '/game' },
        { id: 'tournament-nav', path: '/tournament' },
        { id: 'chat-nav', path: '/chat' },
        { id: 'logout-nav', path: '/logout' },
        { id: 'profile-nav', path: '/profile' },
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
    setUpDataAndStyles();

    // add the handlers to the navbar objects
    for (const route of navigationBarMap) {
        $id(route.id)?.addEventListener('click', () => router(route.path, route?.params));
    }
}