import { routes } from './routes.js';
import { setViewLoading, isViewLoading } from '../abstracts/loading.js';
import { $id, $queryAll } from '../abstracts/dollars.js';
// bind store, auth and other singleton to 'this' in the hooks
import { setNavVisibility } from '../abstracts/nav.js';
import $store from '../store/store.js';
import $auth from '../auth/authentication.js';
import $syncer from '../sync/Syncer.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';
import dollars from '../abstracts/dollars.js';
import { translate, staticTranslator } from '../locale/locale.js';
import { audioPlayer } from '../abstracts/audio.js';
import { historyManager } from './history.js';
import { modalManager } from '../abstracts/ModalManager.js';
import { EventListenerManager } from '../abstracts/EventListenerManager.js';

const simpleObjectToBind = () => {
    return {
        router: router,
        $store: $store,
        $auth: $auth,
        $syncer: $syncer,
        call: call,
        webSocketManager: WebSocketManager,
        translate: translate,
        domManip: dollars,
        audioPlayer: audioPlayer,
    }
}

export const objectToBind = (config, params = null) => {
    let binder = {};
    let {hooks, attributes, methods} = config || {attributes: {}, methods: {}, hooks: {}}

    for (const [key, value] of Object.entries(attributes || {})) {
        binder[key] = value;
    }

    binder = { ...simpleObjectToBind(), ...binder, routeParams: params };

    for (const [key, value] of Object.entries(methods || {})) {
        binder[key] = value.bind(binder);
    }

    return binder;
}

async function getViewHooks(viewName) {
    if (!viewName) return null;

    // Load view hooks
    return await import(`../views/${viewName}/configs.js`).then(conf => conf.default).then(viewHooks => {
        return viewHooks;
    }).catch(err => {
        console.log(`For view ${viewName} there are no hooks! Err: ${err}`);
        return null;
    });
}

async function router(path, params = null, updateHistory = true) {
    if(!path)
        return;
    setViewLoading(true);

    // TODO: prevent router to be called multiple times -> only if the view is loaded
    // ---
    // THE CODE BELOW DOES NOT WORK
    //if (isViewLoading()) {
    //    return;
    //}
    //if($store.fromState('currentRoute') && $store.fromState('currentRoute') === 'loading') {
    //    console.log("Router: View is still loading, ignoring navigation to", path);
    //    return;
    //}
    //$store.commit('setCurrentRoute', 'loading');
    //console.error($store.fromState('currentRoute'));
    //
    // I also create this function isViewLoading but it doesnt work for the first load


    if (path === "/logout") {
        const success = await $auth.logout();
        if (success)
			router("/auth");
		return ;
    }

    // Auth check
    const userAuthenticated = await $auth.isUserAuthenticated();
    if (path === "/barely-responsive") {
        // This view doesnt need auth and also shouldn't redirect to auth
    } else if (userAuthenticated && path === '/auth') {
        // console.log("Redirecting to home");
        path = '/home';
        params = null;
    } else if (!userAuthenticated && path !== '/auth') {
        path = '/auth';
        params = null;
    }

    const viewContainer = $id('router-view');
    const modalContainer = $id('modal-view');

    // find the route that matches the path
    const route = routes.find(route => route.path === path) || {
        path: path,
        view: "404",
        requireAuth: false,
        modals: [],
        backgroundColor: "black"
    };

    // Only update if valid!
    if (route && route.view !== "404")
        $store.commit('setCurrentRoute', route.view);

    // Show hide the nav bar
    if (route.view == "auth" || route.view == "barely-responsive") {
        setNavVisibility(false);
    } else
        setNavVisibility(true);

    EventListenerManager.unlinkEventListenersView(viewContainer.dataset.view);
    // Close all modals before switching routes
    modalManager.destroyAllModals();
    // Now add all modals to the view (the html part)
    modalContainer.innerHTML = "";
    for (const modal of route.modals || []) {
        // console.log("Router: Loading html of modal:", modal);
        modalContainer.innerHTML += await fetch(`./modals/${modal}.html`).then(response => response.text());
    }
    // Setup the js for all modals
    await modalManager.setupAllModalsForView();

    const htmlContent = await fetch(`./${route.view}.html`).then(response => response.text());
    const viewHooks = await getViewHooks(route.view);
    const viewConfigWithoutHooks = objectToBind(viewHooks, params);

    // get the hooks of the last view and call the beforeRouteLeave hook
    const lastViewHooks = await getViewHooks(viewContainer.dataset.view);
    // bind everything except the hooks to the object
    lastViewHooks && await lastViewHooks?.hooks?.beforeRouteLeave?.bind(objectToBind(lastViewHooks))();
    // about to change route
    await viewHooks?.hooks?.beforeRouteEnter?.bind(viewConfigWithoutHooks)();
    // reduce the params to a query string
    let paramsString = params ? Object.keys(params).map(key => `${key}=${params[key]}`).join('&') : null;
    if (paramsString)
        paramsString = "?" + paramsString;

    // DOM manipulation
    await viewHooks?.hooks?.beforeDomInsertion?.bind(viewConfigWithoutHooks)();
    viewContainer.innerHTML = htmlContent;

    // Change background color
    let backgroundColor = "#fcf4e0";    // Default color
    if(route.backgroundColor)
        backgroundColor = route.backgroundColor;
    const backgroundElements = $queryAll(".view-background-color");
    for (let element of backgroundElements)
        element.style.backgroundColor = backgroundColor;

    // Dom manipulation: after DOM insertion
    await viewHooks?.hooks?.afterDomInsertion?.bind(viewConfigWithoutHooks)();
    // set the view name to the container
    viewContainer.dataset.view = route.view;

    // translate static elements on the view
    await staticTranslator(route.view);

    // Update the history
    if(updateHistory)
        historyManager.updateHistory(path, paramsString);

    console.log("Router: View loaded:", route.view);
    setViewLoading(false);
}

export default router;


