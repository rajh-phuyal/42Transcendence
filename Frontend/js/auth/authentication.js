import $store from '../store/store.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';

class Auth {
    constructor() {
        this.isAuthenticated = false;
        this._authCheckPromise = null;
        this._lastCheckTimestamp = 0;
        this._cacheTimeout = 30000; // Cache auth status for 30 seconds, optimal time
        return this;
    }

    clearAuthCache() {
        this._lastCheckTimestamp = 0;
        this._authCheckPromise = null;
    }

    async isUserAuthenticated() {
        const now = Date.now();
        console.log("Checking authentication"); // Debug log

        // Return cached result if within timeout window
        if (this._lastCheckTimestamp && (now - this._lastCheckTimestamp < this._cacheTimeout)) {
            console.log("Using cached auth result:", this.isAuthenticated); // Debug log
            return this.isAuthenticated;
        }

        // If there's already a check in progress, return that promise
        if (this._authCheckPromise) {
            console.log("Using existing auth check promise"); // Debug log
            return this._authCheckPromise;
        }

        // Create new auth check promise
        this._authCheckPromise = (async () => {
            try {
                await call('auth/verify/', 'GET');
                this.isAuthenticated = true;
                console.log("Auth check successful"); // Debug log

                if (!$store.fromState('webSocketIsAlive')) {
                    WebSocketManager.connect();
                }
            } catch (error) {
                console.log("Auth check failed:", error); // Debug log
                this.isAuthenticated = false;
            } finally {
                this._lastCheckTimestamp = now;
                this._authCheckPromise = null;
            }
            return this.isAuthenticated;
        })();

        return this._authCheckPromise;
    }

    async refreshToken() {
        try {
            const response = await fetch('/api/auth/token/refresh/', {
                method: 'POST',
                credentials: 'include', // Important for sending/receiving cookies
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            // No need to store tokens as they're now in HttpOnly cookies
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
            const response = await fetch('/api/auth/verify/', {
                method: 'GET',
                credentials: 'include'
            });

            if (response.status === 401) {
                // Token is expired, try to refresh
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Refresh WebSocket connection after token refresh
                    WebSocketManager.refreshToken();
                    return true;
                }
                return false;
            }

            return response.ok;
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
