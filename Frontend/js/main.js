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
    // TODO: maybe add the class 'sound-button' to the elements that should play a sound
    // oris there a better way to do this?
    const target = event.target.closest(".sound-button");
    if (target) {
        audioPlayer.playSound("toggle"); // Replace with actual sound name
    }
});

// window.addEventListener('popstate', (event) => {
//     const path = event.state?.path || "/";
//     const params = event.state?.params || null;

//     console.log("SUPER EVENT:", event);

//     // make the current params an object
//     router(path, params);
// });


// 1. popstate listener
window.addEventListener('popstate', (event) => {
    console.log('SUPER EVENT', event);
    console.log('popstate triggered', event.state);
    console.log('NAVIGATION:', event.target?.navigation);

    // If we stored route info in the state:
    router(event.state?.route, event.state?.params, false);
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