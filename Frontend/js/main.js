import { $id } from './abstracts/dollars.js';
import { setViewLoading } from './abstracts/loading.js';
import router from './navigation/router.js';
import { webComponents } from './components/components.js';
import { routes } from './routes.js';
import { $store } from './store/store.js';

setViewLoading(true);

try {
    // import all web components
    for (const component of webComponents) {
        import(`./components/${component}.js`);
    }
} catch (error) {
    console.error('Error importing web components:', error);
}

// initilize the nav bar
const navigationBarMap = [
    { id: 'home-nav', path: '/home' },
    { id: 'game-nav', path: '/game' },
    { id: 'tournament-nav', path: '/tournament' },
    { id: 'chat-nav', path: '/chat' },
    { id: 'logout-nav', path: '/logout' },
    { id: 'profile-nav', path: '/profile', params: { id: 1 } },
    { id: 'login-nav', path: '/auth', params: { login: true } },
    { id: 'register-nav', path: '/auth', params: { login: false } }
];

for (const route of navigationBarMap) {
    $id(route.id)?.addEventListener('click', () => router(route.path, route.params));
}

window.addEventListener('popstate', () => {
    router(window.location.pathname)
});

// get the translations for all the registered views
$store.dispatch('loadTranslations', routes.map(route => route.view));

// get the path and call the router
router(window.location.pathname);

// set the loading to false
setViewLoading(false);








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
