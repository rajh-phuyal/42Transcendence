import { $store } from '../store/store.js';

class Auth {
    constructor() {
        // Initialize the state from localStorage if available
        this.jwtToken = $store.fromState('jwtToken');

        // Check if the user is authenticated
        this.isAuthenticated = this.isUserAuthenticated();
    }

    // Check if the user is authenticated
    isUserAuthenticated() {
        return $store.fromState('isAuthenticated') && this.verifyJWTToken();
    }

    // Get the Authorization header with the JWT token
    getAuthHeader() {
        const token = this.jwtToken;
        return token ? `Bearer ${token}` : '';
    }

    authenticate(username, password) {
        call('authentication/login', 'POST', { username, password })
        .then(({ token, user }) => {
            $store.commit('setUser', user);
            $store.commit('setIsAuthenticated', true);
            $store.commit('setJWTToken', token);

            // TODO: need to have a success message on global level
        })
        .catch(error => {
            console.error('Failed to authenticate', error);

            // the view needs to handle the error
            throw error;
        });
    }

    // Logout the user by clearing the JWT token and state
    logout() {
        $store.commit('setUser', null);
        $store.commit('setIsAuthenticated', false);
        $store.commit('setJWTToken', null);
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
