import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id, $on, $off } from './dollars.js';
import { audioPlayer } from '../abstracts/audio.js';

function updateUserInfo() {
    $id('profile-nav-avatar').src = `${window.location.origin}/media/avatars/${$store.fromState("user").avatar}`;
    // Music Sound icons
    // Update icons based on initial settings
    $id("nav-music-icon").src = window.origin + (audioPlayer.musicEnabled
        ? '/assets/game/icons/music-on.png'
        : '/assets/game/icons/music-off.png');

    $id("nav-sound-icon").src = window.origin + (audioPlayer.soundsEnabled
        ? '/assets/game/icons/sound-on.png'
        : '/assets/game/icons/sound-off.png');
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
        { id: 'register-nav', path: '/auth' },
        { id: 'nav-music-icon',
            callback: () => {
                audioPlayer.toggleMusic();
                $id("nav-music-icon").src = window.origin + (audioPlayer.musicEnabled
                    ? '/assets/game/icons/music-on.png'
                    : '/assets/game/icons/music-off.png');
            }
		},
        { id: 'nav-sound-icon',
            callback: () => {
                audioPlayer.toggleSound();
                $id("nav-sound-icon").src = window.origin + (audioPlayer.soundsEnabled
                    ? '/assets/game/icons/sound-on.png'
                    : '/assets/game/icons/sound-off.png');
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
    // TODO: @astein: I guess we don't need this line below since
    // clickig on chat in navbar should not have any params
    // routeFinder('/chat').params = { id: undefined };

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
