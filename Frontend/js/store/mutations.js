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
        presistence: true,
    },
    setWebsocketIsAlive: {
        stateName: 'webSocketIsAlive',
        onUpdate: (state, value) => {
            state.websocketIsAlive = value;
        },
        presistence: false,
    },
	setMarkBook: {
		stateName: 'markbook',
		onUpdate: (state, value) => {
			state.markbook = value;
		},
		presistence: true,
	},
    setCurrentRoute: {
        stateName: 'currentRoute',
        onUpdate: (state, value) => {
            state.currentRoute = value;
        }
    },
    setMusic: {
        stateName: 'music',
        onUpdate: (state, value) => {
            state.music = value;
        },
        presistence: true,
    },
    setSound: {
        stateName: 'sound',
        onUpdate: (state, value) => {
            state.sound = value;
        },
        presistence: true,
    }
};