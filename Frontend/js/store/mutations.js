export const mutations = {
    setUser: {
        stateName: 'user',
        onUpdate: (state, value) => {
            state.user = value;
        },
        persistence: true,
    },
    setIsAuthenticated: {
        stateName: 'isAuthenticated',
        onUpdate: (state, value) => {
            state.isAuthenticated = value;
        },
        persistence: false,
    },
    setJWTTokens: {
        stateName: 'jwtTokens',
        onUpdate: (state, value) => {
            state.jwtTokens = value;
        },
        persistence: true,
    },
    setLocale: {
        stateName: 'locale',
        onUpdate: (state, value) => {
            state.locale = value;
        },
        persistence: true,
    },
    setTranslations: {
        stateName: 'translations',
        onUpdate: (state, value) => {
            state.translations = value;
        },
        persistence: true,
    },
    setWebsocketIsAlive: {
        stateName: 'webSocketIsAlive',
        onUpdate: (state, value) => {
            state.websocketIsAlive = value;
        },
        persistence: false,
    },
	setMarkBook: {
		stateName: 'markbook',
		onUpdate: (state, value) => {
			state.markbook = value;
		},
		persistence: true,
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
        persistence: true,
    },
    setSound: {
        stateName: 'sound',
        onUpdate: (state, value) => {
            state.sound = value;
        },
        persistence: true,
    }
};