import { state } from './states.js';
import { mutations } from './mutations.js';
import { actions } from './actions.js';
import { $getLocal, $setLocal } from '../abstracts/dollars.js';

class Store {
    constructor(initialState, mutations, actions) {
        this.state = { ...initialState };

        // pull from local storage
        const localStore = JSON.parse($getLocal("store")) || {};
        this.state = { ...this.state, ...localStore };

        this.actions = actions;
        this.mutations = mutations;

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

        this.mutations[mutationName]?.method(this.state, value);

        if (!this.mutations[mutationName]?.presistence) return;

        // cleare all the mutations, that have presistence set to false
        let savedObject = {};
        for (const [key, value] of Object.entries(this.mutations)) {
            // setUser -> user using lodash
            const stateKey = key.charAt(3).toLowerCase() + key.slice(4);
            if (value.presistence) {
                savedObject[stateKey] = this.state[stateKey];
            }
        }
        $setLocal("store", JSON.stringify(savedObject));
    }

    dispatch(actionName, payload) {
        this.actions[actionName](this, payload);
    }

    clear() {
        this.state = { ...state };
        $setLocal("store", JSON.stringify(this.state));
    }
}

const $store = new Store(state, mutations, actions);

export default $store;