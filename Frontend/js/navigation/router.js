import { routes } from './routes.js';
import { setViewLoading } from '../abstracts/loading.js';
import { $id } from '../abstracts/dollars.js';
import { $getLocal } from '../abstracts/dollars.js';

// bind store and auth singleton to 'this' in the hooks
import $store from '../store/store.js';
import $auth from '../auth/authentication.js';
import call from '../abstracts/call.js';
import WebSocketManager from '../abstracts/WebSocketManager.js';
//import loading from '../abstracts/loading.js'; TODO this should be added later
import dollars from '../abstracts/dollars.js';
import { translate } from '../locale/locale.js';

const objectToBind = (config, params = null) => {
    let binder = {};
    let {hooks, attributes, methods} = config || {attributes: {}, methods: {}, hooks: {}}

    for (const [key, value] of Object.entries(attributes || {})) {
        binder[key] = value;
    }

    for (const [key, value] of Object.entries(methods || {})) {
        binder[key] = value.bind(binder);
    }

    binder.router = router;
    binder.$store = $store;
    binder.$auth = $auth;
    binder.routeParams = params;
    binder.translate = translate;
    binder.call = call;
	binder.webSocketManager = WebSocketManager;
   // binder.loading = loading;
    binder.domManip = dollars;

    return binder;
}

async function getViewHooks(viewName) {
    if (!viewName) return null;

    return await import(`../views/${viewName}/configs.js`).then(conf => conf.default).then(viewHooks => {
        return viewHooks;
    }).catch(err => {
        console.log(`For view ${viewName} there are no hooks! Err: ${err}`);
        return null;
    });
}

async function router(path, params = null) {
    console.log("Router called with path:", path);
    setViewLoading(true);

    if (_.isEmpty($getLocal("store"))) {
        console.log("Initializing store");
        $store.initializer();
    }
    const userAuthenticated = await $auth.isUserAuthenticated();
    console.log("User authenticated:", userAuthenticated);

    if (userAuthenticated && path === '/auth') {
        console.log("Redirecting to home");
        path = '/home';
    }

    if (!userAuthenticated && path !== '/auth') {
        console.log("Redirecting to auth");
        path = '/auth';
    }

    const viewContainer = $id('router-view');

    // find the route that matches the path
    const route = routes.find(route => route.path === path) || {
        path: path,
        view: "404",
        requireAuth: false,
    };

    const htmlContent = await fetch(`./${route.view}.html`).then(response => response.text());
    const viewHooks = await getViewHooks(route.view);
    const viewConfigWithoutHooks = objectToBind(viewHooks, params);

    // get the hooks of the last view and call the beforeRouteLeave hook
    const lastViewHooks = await getViewHooks(viewContainer.dataset.view);

    // bind everything except the hooks to the object
    lastViewHooks && lastViewHooks?.hooks?.beforeRouteLeave?.bind(objectToBind(lastViewHooks))();

    // about to change route
    viewHooks?.hooks?.beforeRouteEnter?.bind(viewConfigWithoutHooks)();

    // reduce the params to a query string
    params = params ? Object.keys(params).map(key => `${key}=${params[key]}`).join('&') : null;
    const pathWithParams = params ? `${path}?${params}` : path;
    history.pushState({}, 'newUrl', pathWithParams);

    // DOM manipulation
    viewHooks?.hooks?.beforeDomInsertion?.bind(viewConfigWithoutHooks)();
    viewContainer.innerHTML = htmlContent;
    viewHooks?.hooks?.afterDomInsertion?.bind(viewConfigWithoutHooks)();

    // set the view name to the container
    viewContainer.dataset.view = route.view;

    setViewLoading(false);
}

export default router;