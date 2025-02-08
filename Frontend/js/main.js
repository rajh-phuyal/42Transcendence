import $nav from './abstracts/nav.js';
import { setViewLoading } from './abstracts/loading.js';
import router from './navigation/router.js';
import { webComponents } from './components/components.js';
import { routes } from './navigation/routes.js';
import $store from './store/store.js';
import WebSocketManager from './abstracts/WebSocketManager.js';
import $callToast from './abstracts/callToast.js';
import { translate } from './locale/locale.js';
import { audioPlayer } from './abstracts/audio.js';
setViewLoading(true);

try {
    // import all web components
    for (const component of webComponents) {
        import(`./components/${component}.js`);
    }
} catch (error) {
    console.error('Error importing web components:', error);
}

window.addEventListener("click", (event) => {
    const target = event.target.closest(".sound-button");
    console.log("Wanna play sound", target);
    if (target) {
        audioPlayer.playSound("toggle"); // Replace with actual sound name
    }
});

window.addEventListener('popstate', () => {
    router(window.location.pathname)
});

// get the translations for all the registered views
$store.dispatch('loadTranslations', routes.map(route => route.view));

// Initializes the nav bar
$nav();


// go to path only after the translations are loaded
$store.addMutationListener('setTranslations', () => {
    // get the current route and its params
    const currentRoute = window.location.pathname;
    const currentParams = window.location.search;

    // make the current params an object
    const currentParamsObject = Object.fromEntries(new URLSearchParams(currentParams));

    router(currentRoute, currentParamsObject);

    // set the loading to false
    setViewLoading(false);
});

let setInervalId = undefined;
$store.addMutationListener('setWebSocketIsAlive', (state) => {
    if (state) {
        console.log("Web socket is connected!");
        if (setInervalId) {
            $callToast("success", translate("global:main", "connectionReestablished"))
            clearInterval(setInervalId);
            setInervalId = undefined;
        }
    } else {
        console.log("Web socket is disconnected!");
        if (!setInervalId && $store.fromState('isAuthenticated')) {
            $callToast("error", translate("global:main", "connectionError"))
            setInervalId = setInterval(() => {
                WebSocketManager.connect();
            }, 2000);
        }
    }
});


/* listen to nav- search bar */
window.addEventListener('select-user-nav', (event) => {
    router('/profile', { id: event.detail.user.id });
});


/* DESABLE ZOOM*/

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && (event.key === '+' || event.key === '-' || event.key === '=')) {
        event.preventDefault();
    }
});

document.addEventListener('wheel', function(event) {
    if (event.ctrlKey) {
        event.preventDefault();
    }
}, { passive: false });
