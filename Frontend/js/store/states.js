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
    translations: {},
    webSocketIsAlive: false,
};
