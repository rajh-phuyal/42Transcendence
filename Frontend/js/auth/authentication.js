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

    isUserAuthenticated() {
        // return $store.fromState('isAuthenticated');
        return $store.fromState('isAuthenticated') && this.verifyJWTToken();
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
        return this.jwtToken ? `Bearer ${this.jwtToken}` : undefined;
    }

    async verifyJWTToken() {
        const token = this.jwtToken;
        if (!token) return false;

        const [header, payload, signature] = token.split('.');
        if (!header || !payload || !signature) return false;

        try {
            const { exp } = JSON.parse(atob(payload));
            if (Date.now() >= exp * 1000) {
                const refreshed = await this.refreshToken();
                return refreshed;
            }
        } catch (e) {
            console.error('Error verifying token:', e);
            const refreshed = await this.refreshToken();
            return refreshed;
        }

        return true;
    }
}

// Create a single global instance of the Auth class
const $auth = new Auth();

export default $auth;
