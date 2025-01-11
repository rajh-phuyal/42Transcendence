import $store from '../store/store.js';
import $syncer from '../sync/Syncer.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';

class Auth {
    constructor() {
        this.isAuthenticated = false;
        this._lastCheckTimestamp = 0;
        this._cacheTimeout = 10000; // 10, sec, optimal for UX and verification
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

    async logout(broadcast = true) {
        try {
            console.log("Logging out...");
            const response = await call('auth/logout/', 'POST', null, true);
            console.log("Logout response", response);

            if (response.statusCode !== 200) {
                return false;
            }

            // Clear all auth-related state
            this.clearAuthCache();
            this.isAuthenticated = false;
            $store.commit('setIsAuthenticated', false);
            WebSocketManager.disconnect();
            $store.clear();

            if (broadcast) {
                // Broadcast logout to other tabs
                $syncer.broadcast("authentication-state", { logout: true });
            }

            // Don't redirect here, let the functional route handle it
            return true;
        } catch (error) {
            console.error('Logout error:', error);
            return false;
        }
    }
}

const $auth = new Auth();
export default $auth;
