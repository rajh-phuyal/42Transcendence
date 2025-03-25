import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id, $on, $off } from './dollars.js';
import { audioPlayer } from '../abstracts/audio.js';
import { translate } from '../locale/locale.js';

function updateUserInfo() {
    $id('nav-avatar').src = `${window.location.origin}/media/avatars/${$store.fromState("user").avatar}`;
    // Music Sound icons
    // Add a mutation listener for music and sound
    $store.addMutationListener('setMusic', (music) => {
        audioPlayer.toggleMusic();
    });
    $store.addMutationListener('setSound', (sound) => {
        audioPlayer.toggleSound();
    });
    // Set the music and sound icons
    audioPlayer.toggleMusic();
    audioPlayer.toggleSound();
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
 *     params: { id: 1 }
 * }
 */
export default function $nav(navigationPathParams = null) {
    // nav bar route to Dom elements map
    const navigationBarMap = [
        { id: 'nav-home', path: '/home' },
        { id: 'nav-chat', path: '/chat' },
        { id: 'nav-avatar', path: '/profile' },
        { id: 'nav-music',
            callback: () => {
                let music = $store.fromState('music');
                $store.commit('setMusic', !music);
            }
		},
        { id: 'nav-sound',
            callback: () => {
                let sound = $store.fromState('sound');
                $store.commit('setSound', !sound);
            }
        }
    ];

    // only update the route params if the navigationPathParams is provided
    if (navigationPathParams) {
        updateRouteParams(navigationPathParams, navigationBarMap);
        return;
    }

    // routes with params
    const routeFinder = (path) => navigationBarMap.find(route => route.path === path);

    routeFinder('/profile').params = { id: $store.fromState("user").id };

    // additional data and styles
    styleUpdateMap?.[routeFinder('/profile').path]?.();

    // Initial setup of handlers
    for (const route of navigationBarMap) {
        const navbarObject = $id(route.id);
        if (!navbarObject) continue;

        // Remove previous handlers
        if (navbarObject._clickHandler) {
            $off(navbarObject, 'click', navbarObject._clickHandler);
        }

        // Set up new event listener
        if (route.callback) {
            navbarObject._clickHandler = route.callback;
        } else if (route.path) {
            navbarObject._clickHandler = () => router(route.path, route?.params);
        }

        $on(navbarObject, 'click', navbarObject._clickHandler);
    }
}
