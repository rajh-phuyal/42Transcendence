const state = {
    user: {
        id: undefined,
        username: undefined,
    },
    isAuthenticated: false,
    jwtToken: undefined,
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
    setJWTToken: {
        method: (state, value) => {
            state.jwtToken = value;
        },
        presistence: true,
    }
};

export { state, mutations };