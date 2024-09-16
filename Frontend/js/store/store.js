import { state, mutations } from './states.js';
import { $getLocal, $setLocal, $setSession } from '../abstracts/dollars.js';

class Store {
    constructor(initialState) {
        this.state = { ...initialState };

        // pull from local storage
        const localStore = JSON.parse($getLocal("store")) || {};
        this.state = { ...this.state, ...localStore };

        this.mutationListeners = [];
    }

    fromState(key) {
        return this.state[key];
    }

    mutationListeners(mutationName, action) {
        this.mutationListeners.push({
            mutationName: mutationName,
            action: action
        });
    }

    notifyListeners(mutationName) {
        this.mutationListeners
            .filter(listener => listener.mutationName === mutationName)
            .forEach(listener => listener.action(this.state));
    }

    commit(mutationName, value) {
        this.notifyListeners(mutationName);

        mutations[mutationName]?.method(this.state, value);

        if (!mutations[mutationName]?.presistence) return;

        $setLocal("store", JSON.stringify(this.state));
    }

    clear() {
        this.state = { ...state };
        $setLocal("store", JSON.stringify(this.state));
    }
}

const $store = new Store(state);

export default $store;