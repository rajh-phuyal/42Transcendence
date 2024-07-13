import { $id } from './dollars.js';
import router from './navigation/router.js';

// initilize the nav bar
const navigationBarMap = [
    { id: 'home-nav', path: '/home' },
    { id: 'game-nav', path: '/game' },
    { id: 'tornament-nav', path: '/tornament' },
    { id: 'chat-nav', path: '/chat' },
    { id: 'profile-nav', path: '/profile' },
    { id: 'login-nav', path: '/auth', params: { login: true } },
    { id: 'register-nav', path: '/auth', params: { login: false } }
];

for (const route of navigationBarMap) {
    $id(route.id)?.addEventListener('click', () => router(route.path, route.params));
}

// get the path and call the router
router(window.location.pathname);