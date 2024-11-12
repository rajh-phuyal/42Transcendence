import $store from '../store/store.js';
import router from '../navigation/router.js';
import { $id } from '../abstracts/dollars.js';

export default function $nav() {
    // initilize the nav bar
    const navigationBarMap = [
        { id: 'home-nav', path: '/home' },
        { id: 'game-nav', path: '/game' },
        { id: 'tournament-nav', path: '/tournament' },
        { id: 'chat-nav', path: '/chat' },
        { id: 'logout-nav', path: '/logout' },
        { id: 'profile-nav', path: '/profile', params: { id: $store.fromState("user").id } },
        { id: 'login-nav', path: '/auth', params: { login: true } },
        { id: 'register-nav', path: '/auth', params: { login: false } }
    ];
    
    for (const route of navigationBarMap) {
        console.log("yoooo", route.id, route.params, route.path);
        $id(route.id)?.addEventListener('click', () => router(route.path, route.params));
    }
}