import { router } from './router.js';

// initilize the nav bar
document.getElementById('home-nav').addEventListener('click', () => router('/home'));
document.getElementById('battle-nav').addEventListener('click', () => router('/battle'));
document.getElementById('login-nav').addEventListener('click', () => router('/auth', { login: true }));
document.getElementById('register-nav').addEventListener('click', () => router('/auth', { login: false }));
