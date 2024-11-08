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
    setJWTTokens: {
        stateName: 'jwtTokens',
        onUpdate: (state, value) => {
            state.jwtTokens = value;
        },
        presistence: true,
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
};