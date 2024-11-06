import $store from '../store/store.js';
import call from '../abstracts/call.js';

class Auth {
    constructor() {
        // Initialize the state from localStorage if available
        this.jwtToken = $store.fromState('jwtTokens').access;

        // Check if the user is authenticated
        this.isAuthenticated = this.isUserAuthenticated();

        return this;
    }

    isUserAuthenticated() {
        return $store.fromState('isAuthenticated') || false;
        // TODO:  after the refresh issue is fixed, USE THE LINE BELOW
        // return $store.fromState('isAuthenticated') && this.verifyJWTToken();
    }

    authenticate(username, password) {
        return call('auth/login/', 'POST', { username: username, password: password });
    }

    createUser(username, password) {
        return call('auth/register/', 'POST', { username: username, password: password });
    }

    async refreshToken() {
        return await call('auth/token/refresh/', 'POST', { refresh: $store.fromState('jwtTokens').refresh }).then((response) => {
            this.jwtToken = response.access;

            $store.commit('setJWTTokens', {
                ...$store.fromState('jwtTokens'),
                access: this.jwtToken
            });

            return true;
        })
        .catch((error) => {
            console.error('Error refreshing token:', error);
            this.logout();
            return false;
        });
    }

    logout() {
        $store.clear();
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
