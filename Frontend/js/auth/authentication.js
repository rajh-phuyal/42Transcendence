import { $store } from '../store/store.js';
import call from '../abstracts/call.js';

class Auth {
    constructor() {
        // Initialize the state from localStorage if available
        this.jwtToken = $store.fromState('jwtToken');

        // Check if the user is authenticated
        this.isAuthenticated = this.isUserAuthenticated();

        return this;
    }

    // Check if the user is authenticated
    isUserAuthenticated() {
        return $store.fromState('isAuthenticated') && this.verifyJWTToken();
    }

    authenticate(username, password) {
        return call('auth/login/', 'POST', { username: username, password: password });
    }

    createUser(username, password) {
        return call('auth/register/', 'POST', { username: username, password: password });
    }

    // Logout the user by clearing the JWT token and state
    logout() {
        $store.commit('setUser', null);
        $store.commit('setIsAuthenticated', false);
        $store.commit('setJWTToken', null);
    }

    // Get the Authorization header with the JWT token
    getAuthHeader() {
        return this.jwtToken ? `Bearer ${this.jwtToken}` : undefined;
    }

    // Verify the JWT token's validity
    verifyJWTToken() {
        const token = this.jwtToken;
        if (!token) return false;

        const [header, payload, signature] = token.split('.');
        if (!header || !payload || !signature) return false;

        try {
            const { exp } = JSON.parse(atob(payload));
            if (Date.now() >= exp * 1000) {
                this.logout();
                return false;
            }
        } catch (e) {
            // TODO: try to refresh the token
            console.error('Invalid token', e);
            this.logout();
            return false;
        }
        return true;
    }
}

// Create a single global instance of the Auth class
const $auth = new Auth();

export { $auth };
