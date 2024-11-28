import $nav from './abstracts/navigationInit.js';
import { setViewLoading } from './abstracts/loading.js';
import router from './navigation/router.js';
import { webComponents } from './components/components.js';
import { routes } from './navigation/routes.js';
import $store from './store/store.js';
import WebSocketManager from './abstracts/WebSocketManager.js';
import $callToast from './abstracts/callToast.js';

setViewLoading(true);

try {
    // import all web components
    for (const component of webComponents) {
        import(`./components/${component}.js`);
    }
} catch (error) {
    console.error('Error importing web components:', error);
}

// Initializes the nav bar
$nav();


window.addEventListener('popstate', () => {
    router(window.location.pathname)
});

// go to path only after the translations are loaded
$store.addMutationListener('setTranslations', (state) => {
    router(window.location.pathname);

    // set the loading to false
    setViewLoading(false);
});

let setInervalId = undefined;
$store.addMutationListener('setWebSocketIsAlive', (state) => {
    console.log('setWebSocketIsAlive', state);
    if (state) {
        console.log("Web socket is connected!");
        if (setInervalId) {
            $callToast("success", "Connection re-established. What ever...")
            clearInterval(setInervalId);
            setInervalId = undefined;
        }
    } else {
        console.log("Web socket is disconnected!");
        if (!setInervalId && $store.fromState('isAuthenticated')) {
            $callToast("error", "Connection error. But remember that the overlords are STILL watching...")
            setInervalId = setInterval(() => {
                console.log('retrying connection');
                WebSocketManager.connect();
            }, 2000);
        }
    }
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
