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
import { zoomIn } from './views/barely-responsive/methods.js';
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
    // Handle sound button clicks
    let soundClasses = [
        ".click-sound",
        ".modal-button",
        ".mention-user",
        ".mention-game",
        ".mention-tournament"];
    let target = null;
    for (let i = 0; i < soundClasses.length; i++) {
        target = event.target.closest(soundClasses[i]);
        if (target) break;
    }
    if (target) {
        audioPlayer.playSound("click");
    }
});

// For the Back/Forward buttons in the browser (aka history navigation)
window.addEventListener('popstate', (event) => {
    // The state stored in pushState will be available as `event.state`
    const state = event.state;
    if (state && state.path) {
        // transform params string back to object: "id=1&name=John" => { id: 1, name: "John" }
        let paramsObject = {};
        if (state.params) {
            // First remove the question at index 1 if it exists
            if (state.params[0] === '?')
                state.params = state.params.slice(1);
            paramsObject = state.params
                .split('&')                 // Split by '&' if there are multiple parameters (but I guess we don't have this)
                .reduce((acc, param) => {
                  const [key, value] = param.split('=');    // Split each key-value pair
                  acc[key] = decodeURIComponent(value);     // Assign the key-value pair to the accumulator
                  return acc;
                }, {});
        }
        router(state.path, paramsObject, false);
    }
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

    router(currentRoute, currentParamsObject, false);

    // set the loading to false
    setViewLoading(false);
});

let setInervalId = undefined;
$store.addMutationListener('setWebSocketIsAlive', (state) => {
    if (state) {
        if (setInervalId) {
            $callToast("success", translate("global:main", "connectionReestablished"))
            clearInterval(setInervalId);
            setInervalId = undefined;
        }
    } else {
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


window.onresize = () => {
	if (window.outerHeight < 1020 || window.outerWidth < 1020){
        zoomIn(window.outerHeight, window.outerWidth);
        if (window.location.pathname != "/barely-responsive") {
            $store.commit("setMarkBook", window.location.pathname);
            router("/barely-responsive");
        }
	} else if (window.outerHeight >= 1020 && window.outerWidth >= 1020
		&& window.location.pathname == "/barely-responsive") {
			const path = $store.state.markbook;
			$store.commit("setMarkBook", "");
			router(path);
		}
}