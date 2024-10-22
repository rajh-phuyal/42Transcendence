export const state = {
    user: {
        id: undefined,
        username: undefined,
    },
    isAuthenticated: false,
    jwtTokens: {
        access: undefined,
        refresh: undefined,
    },
    locale: 'en-US',
    translations: {}
};

const mutations = {
    setUser: {
        method: (state, value) => {
            state.user = value;
        },
        presistence: true,
    },
    setIsAuthenticated: {
        method: (state, value) => {
            state.isAuthenticated = value;
        },
        presistence: false,
    },
    setJWTTokens: {
        method: (state, value) => {
            state.jwtTokens = value;
        },
        presistence: true,
    },
    setLocale: {
        method: (state, value) => {
            state.locale = value;
        },
        presistence: true,
    },
    setTranslations: {
        method: (state, value) => {
            state.translations = value;
        },
        presistence: true,
    },
};

export { state, mutations };
