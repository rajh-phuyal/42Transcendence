import $store from '../store/store.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';

class Auth {
    constructor() {
        // Initialize the state from localStorage if available
        this.jwtToken = $store.fromState('jwtTokens').access;

        // Check if the user is authenticated
        this.isAuthenticated = this.isUserAuthenticated();

        return this;
    }

    async isUserAuthenticated() {
        if (await this.verifyJWTToken() && !$store.fromState('webSocketIsAlive'))
            WebSocketManager.connect($store.fromState('jwtTokens').access);
            
        return await this.verifyJWTToken();
    }

    authenticate(username, password) {
        return call('auth/login/', 'POST', { username: username, password: password });
    }

    createUser(username, password) {
        return call('auth/register/', 'POST', { username: username, password: password });
    }

    async refreshToken() {
        return await call('auth/token/refresh/', 'POST', { refresh: $store.fromState('jwtTokens').refresh });
        //TODO: Refresh the WebSocket connection with the new token
    }

    logout() {
        $store.clear();
		WebSocketManager.disconnect();
    }

    getAuthHeader() {
        return $store.fromState('jwtTokens').access ? `Bearer ${$store.fromState('jwtTokens').access}` : undefined;
    }

    async verifyJWTToken() {
        const token = $store.fromState('jwtTokens').access;
        if (!token) return false;

        const [header, payload, signature] = token.split('.');
        if (!header || !payload || !signature) return false;

        try {
            const { exp } = JSON.parse(atob(payload));
            if (Date.now() >= exp * 1000) {
                this.logout(); //? Token has expired, for now just log out the user
                // TODO: fix the refresh issue here
                // const refreshed = await this.refreshToken();
                // return refreshed;
            }
        } catch (e) {
            console.error('Error verifying token:', e);
            this.logout(); //? Token is invalid, for now just log out the user
            // TODO: fix the refresh issue here
            // const refreshed = await this.refreshToken();
            // return refreshed;
        }

        return true;
    }
}

// Create a single global instance of the Auth class
const $auth = new Auth();

export default $auth;
