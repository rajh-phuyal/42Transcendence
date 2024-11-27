import $store from '../store/store.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';

class Auth {
    constructor() {
        this.isAuthenticated = false;
        this._lastCheckTimestamp = 0;
        this._cacheTimeout = 30000; // 30, sec, optimal for UX
        return this;
    }

    clearAuthCache() {
        this._lastCheckTimestamp = 0;
    }

    async isUserAuthenticated() {
        const now = Date.now();
        console.log("Checking authentication");

        // Return cached result if within timeout window
        if (this._lastCheckTimestamp && (now - this._lastCheckTimestamp < this._cacheTimeout)) {
            console.log("Using cached auth result:", this.isAuthenticated);
            return this.isAuthenticated;
        }

        // Create new auth check promise
        return await (async () => {
            try {
                const response = await call('auth/verify/', 'GET', null, false);
                if (!response.isAuthenticated) {
                    return false;
                }

                this.isAuthenticated = response.isAuthenticated;
                $store.commit('setIsAuthenticated', this.isAuthenticated);
                console.log("Auth check successful");

                if (this.isAuthenticated && !$store.fromState('webSocketIsAlive')) {
                    console.log("Connecting WebSocket");
                    WebSocketManager.connect();
                }

                this._lastCheckTimestamp = now;
            } catch (error) {
                console.log("Auth check failed:", error);
                this.isAuthenticated = false;
                this.clearAuthCache();
            }

            return this.isAuthenticated;
        })();
    }

    async refreshToken() {
        try {
            const response = await call('auth/token/refresh/', 'POST');

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            return true;
        } catch (error) {
            console.error('Error refreshing token:', error);
            this.logout();
            return false;
        }
    }

    /**
     * Verify the JWT token
     * @returns {boolean} True if the token is valid, false otherwise
     */
    async verifyJWTToken() {
        try {
            const response = await call('auth/verify/', 'GET');

            if (!response.isAuthenticated) {
                // Token is expired, try to refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    $store.commit('setIsAuthenticated', true);
                    console.log("Reconnecting WebSocket");
                    WebSocketManager.reconnect();
                    return true;
                }

                throw new Error("Token is expired and refresh failed");
            }

            return response.isAuthenticated;
        } catch (e) {
            console.error('Error verifying token:', e);
            this.logout();
            return false;
        }
    }

    authenticate(username, password) {
        return call('auth/login/', 'POST',
            { username: username, password: password }
        );
    }

    createUser(username, password) {
        return call('auth/register/', 'POST',
            { username: username, password: password }
        );
    }

    async logout() {
        try {
            await call('auth/logout/', 'POST', null);
            this.clearAuthCache();
            this.isAuthenticated = false;
            $store.clear();
            WebSocketManager.disconnect();
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
}

const $auth = new Auth();
export default $auth;
