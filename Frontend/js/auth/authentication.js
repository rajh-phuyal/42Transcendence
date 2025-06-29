import $store from '../store/store.js';
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

        // Return cached result if within timeout window
        if (this._lastCheckTimestamp && (now - this._lastCheckTimestamp < this._cacheTimeout)) {
            return this.isAuthenticated;
        }

        // Create new auth check promise
        return await (async () => {
            this.isAuthenticated = false;
            let response = null;

            try {
                response = await call('auth/verify/', 'GET', null, false);
                this.isAuthenticated = response.isAuthenticated;
                if (response && response.locale)
                    $store.commit('setLocale', response?.locale);
            } catch (error) {
                this.isAuthenticated = false;
                this.clearAuthCache();
            } finally {
                if (!this.isAuthenticated) {
                    try {
                        if (!await this.refreshToken()) {
                            this._lastCheckTimestamp = now;
                            return false;
                        }
                    } catch (error) {
                        this._lastCheckTimestamp = now;
                        return false;
                    }
                    this.isAuthenticated = true;
                }
            }
            $store.commit('setIsAuthenticated', this.isAuthenticated);
            if (this.isAuthenticated && !$store.fromState('webSocketIsAlive')) {
                WebSocketManager.connect();
            }
            this._lastCheckTimestamp = now;
            return this.isAuthenticated;
        })();
    }

    async refreshToken() {
        try {
            const response = await call('auth/token/refresh/', 'POST', null, false);
            return response.statusCode === 200;
        } catch (error) {
            return false;
        }
    }

    async authenticate(username, password) {
        return await call('auth/login/', 'POST',
            { username: username, password: password }
        );
    }

	async createUser(username, password, language = 'en-US') {
		return await call(`auth/register/?language=${language}`, 'POST',
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
            await $store.clear();

            //if (broadcast) {
            //    // Broadcast logout to other tabs
            //    //$syncer.broadcast("authentication-state", { logout: true });
            //}

            // Don't redirect here, let the router handle it
            return true;
        } catch (error) {
            console.error('Logout error:', error);
            return false;
        }
    }
}

const $auth = new Auth();
export default $auth;
