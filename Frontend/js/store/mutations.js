export const mutations = {
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
    setJWTToken: {
        method: (state, value) => {
            state.jwtToken = value;
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
        presistence: false,
    },
};