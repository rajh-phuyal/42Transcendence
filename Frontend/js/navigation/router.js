import { routes } from './routes.js';
import { functionalRoutes } from './functionalRoutes.js';
import { setViewLoading } from '../abstracts/loading.js';
import { $id } from '../abstracts/dollars.js';
// bind store, auth and other singleton to 'this' in the hooks
import $store from '../store/store.js';
import $auth from '../auth/authentication.js';
import $syncer from '../sync/Syncer.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';
// import loading from '../abstracts/loading.js'; TODO this should be added later
import dollars from '../abstracts/dollars.js';
import { translate } from '../locale/locale.js';
import { audioPlayer } from '../abstracts/audio.js';
import { modalManager } from '../abstracts/ModalManager.js';
import { EventListenerManager } from '../abstracts/EventListenerManager.js';

const simpleObjectToBind = () => {
    return {
        router: router,
        $store: $store,
        $auth: $auth,
        $syncer: $syncer,
        call: call,
        // loading: loading,
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

async function router(path, params = null) {
    setViewLoading(true);

    // check for routes pre authentication check
    const functionalRoute = functionalRoutes.find(route => route.path === path);
    if (functionalRoute && !functionalRoute?.requireAuth) {
        await functionalRoute.execute.bind(simpleObjectToBind())();
        setViewLoading(false);
        return;
    }

    const userAuthenticated = await $auth.isUserAuthenticated();
    console.log("User authenticated:", userAuthenticated);

    if (path === "/barely-responsive") {
        console.log("TODO: check if we need this if!");
    } else if (userAuthenticated && path === '/auth') {
        console.log("Redirecting to home");
        path = '/home';
        params = null;
    }

    else if (!userAuthenticated && path !== '/auth') {
        console.log("Redirecting to auth");
        path = '/auth';
        params = null;
    }

    // execute the functional route which needs auth
    if (functionalRoute) {
        await functionalRoute.execute.bind(simpleObjectToBind())();
        setViewLoading(false);
        return;
    }

    const viewContainer = $id('router-view');
    const modalContainer = $id('modal-view');

    // find the route that matches the path
    const route = routes.find(route => route.path === path) || {
        path: path,
        view: "404",
        requireAuth: false,
        modals: [],
    };

    if (route.view == "auth" || route.view == "barely-responsive") {
        let nav = document.getElementById('navigator');
        nav.style.display = 'none';
    }

    EventListenerManager.unlinkEventListenersView(viewContainer.dataset.view);
    // Close all modals before switching routes
    modalManager.destroyAllModals();
    // Now add all modals to the view (the html part)
    modalContainer.innerHTML = "";
    for (const modal of route.modals || []) {
        console.log("Router: Loading html of modal:", modal);
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
    params = params ? Object.keys(params).map(key => `${key}=${params[key]}`).join('&') : null;
    const pathWithParams = params ? `${path}?${params}` : path;
    history.pushState({}, 'newUrl', pathWithParams);
    // DOM manipulation
    await viewHooks?.hooks?.beforeDomInsertion?.bind(viewConfigWithoutHooks)();
    viewContainer.innerHTML = htmlContent;
    await viewHooks?.hooks?.afterDomInsertion?.bind(viewConfigWithoutHooks)();
    // set the view name to the container
    viewContainer.dataset.view = route.view;
    setViewLoading(false);
}

export default router;