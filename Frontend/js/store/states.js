const state = {
    user: {
        id: undefined,
        username: undefined,
    },
    isAuthenticated: false,
    jwtTokens: {
        access: undefined,
        refresh: undefined,
    },
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
};

export { state, mutations };