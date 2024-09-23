import { routes } from './routes.js';
import { setViewLoading } from '../abstracts/loading.js';
import { $id } from '../abstracts/dollars.js';

// bind store and auth singleton to 'this' in the hooks
import $store from '../store/store.js';
import $auth from '../auth/authentication.js';

const objectToBind = (config) => {
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
    setViewLoading(true); // later this responsibility will the that of the view

    if ($auth.isUserAuthenticated() && path === '/auth') {
        path = '/home';
    }

    if (!$auth.isUserAuthenticated() && path !== '/auth') {
        path = '/auth';
        params = { login: true };
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
    const viewConfigWithoutHooks = objectToBind(viewHooks);

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

    setViewLoading(false);

    // set the view name to the container
    viewContainer.dataset.view = route.view;
}

export default router;