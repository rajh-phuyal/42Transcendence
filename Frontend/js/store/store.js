import { state } from './states.js';
import { mutations } from './mutations.js';
import { actions } from './actions.js';
import { $getLocal, $removeLocal, $setLocal } from '../abstracts/dollars.js';
import { routes } from '../navigation/routes.js';

class Store {
    constructor(initialState, mutations, actions) {
        this.initialState = initialState;
        this.mutations = mutations;
        this.actions = actions;
        this.mutationListeners = [];
        this.initializer()
    }

    initializer() {
        // console.log("Initializing store: initializer");
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

    removeMutationListener(mutationName) {
        this.mutationListeners = _.filter(this.mutationListeners, listener => listener.mutationName !== mutationName);
    }

    notifyListeners(mutationName, newState) {
        this.mutationListeners
            .filter(listener => listener.mutationName === mutationName)
            .forEach(listener => listener.action(newState));
    }

    commit(mutationName, value) {
        this.mutations[mutationName]?.onUpdate(this.state, value);

        this.notifyListeners(mutationName, value);

        if (!this.mutations[mutationName]?.persistence) return;

        // clear all the mutations, that have persistence set to false
        let savedObject = {};
        for (const value of _.values(this.mutations)) {
            const stateKey = value.stateName;

            if (value.persistence) {
                savedObject[stateKey] = this.state[stateKey];
            }
        }

        $setLocal("store", JSON.stringify(savedObject));
    }

    async dispatch(actionName, payload) {
        await this.actions[actionName](this, payload);
    }

    async clear() {
        // Reset to initial state
        this.state = { ...this.initialState };
        $removeLocal("store");
        await this.dispatch('loadTranslations', routes.map(route => route.view));
    }
}

const $store = new Store(state, mutations, actions);

export default $store;