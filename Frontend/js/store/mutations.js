export const mutations = {
    setUser: {
        stateName: 'user',
        onUpdate: (state, value) => {
            state.user = value;
        },
        presistence: true,
    },
    setIsAuthenticated: {
        stateName: 'isAuthenticated',
        onUpdate: (state, value) => {
            state.isAuthenticated = value;
        },
        presistence: false,
    },
    setLocale: {
        stateName: 'locale',
        onUpdate: (state, value) => {
            state.locale = value;
        },
        presistence: true,
    },
    setTranslations: {
        stateName: 'translations',
        onUpdate: (state, value) => {
            state.translations = value;
        },
        presistence: false,
    },
    setWebsocketIsAlive: {
        stateName: 'webSocketIsAlive',
        onUpdate: (state, value) => {
            state.websocketIsAlive = value;
        },
        presistence: false,
    }
};