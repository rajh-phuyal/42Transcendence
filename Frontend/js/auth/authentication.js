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
        const isAuthenticated = await this.verifyJWTToken();

        if (isAuthenticated && !$store.fromState('webSocketIsAlive'))
            WebSocketManager.connect($store.fromState('jwtTokens').access);

        return isAuthenticated;
    }

    authenticate(username, password) {
        return call('auth/login/', 'POST', { username: username, password: password });
    }

    createUser(username, password) {
        return call('auth/register/', 'POST', { username: username, password: password });
    }

    async refreshToken() {
        try {
            return await call('auth/token/refresh/', 'POST', { refresh: $store.fromState('jwtTokens').refresh });
        } catch (e) {
            console.error("Refresh token error:", e);
            this.logout();
            return false;
        }
    }

    logout() {
        $store.clear();
		WebSocketManager.disconnect();
    }

    getAuthHeader() {
        return $store.fromState('jwtTokens').access ? `Bearer ${$store.fromState('jwtTokens').access}` : undefined;
    }

    timeExpired(exp) {
        return Date.now() >= exp * 1000;
    }

    /**
     * Verify the JWT token
     * @returns {boolean} True if the token is valid, false otherwise
     */
    async verifyJWTToken() {
        const token = $store.fromState('jwtTokens').access;
        if (!token) return false;

        const [header, payload, signature] = token.split('.');
        if (!header || !payload || !signature) return false;

        try {
            const { exp } = JSON.parse(atob(payload));
            if (this.timeExpired(exp)) {
                const refreshed = await this.refreshToken();

                // update the jwt tokens in the store
                $store.commit('setJwtTokens', {
                    ...$store.fromState('jwtTokens'),
                    access: refreshed.access,
                });

                // reload WebSocket connection with the new token
                WebSocketManager.refreshToken(refreshed.access);

                return true;
            }
        } catch (e) {
            console.error('Error verifying token:', e);
            this.logout();
        }

        return true;
    }
}

// Create a single global instance of the Auth class
const $auth = new Auth();

export default $auth;
