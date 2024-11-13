import { state } from './states.js';
import { mutations } from './mutations.js';
import { actions } from './actions.js';
import { $getLocal, $setLocal } from '../abstracts/dollars.js';

class Store {
    constructor(initialState, mutations, actions) {
        this.initialState = initialState;
        this.mutations = mutations;
        this.actions = actions;
        this.mutationListeners = [];
        this.initializer();
    }

    initializer() {
        this.state = { ...this.initialState };
        
        // pull from local storage
        const localStore = JSON.parse($getLocal("store")) || {};
        this.state = { ...this.state, ...localStore };
    }

    fromState(key) {
        return this.state[key];
    }

    addMutationListener(mutationName, action) {
        this.mutationListeners.push({
            mutationName: mutationName,
            action: action
        });
    }

    notifyListeners(mutationName, newState) {
        this.mutationListeners
            .filter(listener => listener.mutationName === mutationName)
            .forEach(listener => listener.action(newState));
    }

    commit(mutationName, value) {
        this.mutations[mutationName]?.onUpdate(this.state, value);

        this.notifyListeners(mutationName, value);

        if (!this.mutations[mutationName]?.presistence) return;

        // clear all the mutations, that have presistence set to false
        let savedObject = {};
        for (const value of _.values(this.mutations)) {
            const stateKey = value.stateName;

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