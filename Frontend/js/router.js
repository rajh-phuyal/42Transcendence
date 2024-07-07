// import { routes } from './routes'; // later when modules is resolved, this will be uncommented

const PATH_TO_VIEWS = "/html/";

const routes = [
    {
        path: "/",
        view: "home.html",
        requireAuth: true
    },
    {
        path: "/home",
        view: "home.html",
        requireAuth: true
    },
    {
        path: "/battle",
        view: "battle.html",
        requireAuth: true
    },
    {
        path: "/tornament",
        view: "battle.html",
        requireAuth: true
    },
    {
        path: "/profile",
        view: "profile.html",
        requireAuth: true
    },
    {
        path: "/chat",
        view: "chat.html",
        requireAuth: true
    },
    {
        path: "/auth",
        view: "auth.html",
        requireAuth: false,
    },
];


/* the navigation handler */
/* also does the authentication checks on routes that require auth */

function handelViewScripts(content) {
    const temp = document.createElement('div');
    temp.innerHTML = content;

    let config = null;
    const scripts = temp.querySelectorAll('script');

    scripts.forEach(script => {
        const hasConfig = JSON.parse(script.getAttribute('data-view-config') || 'false');
        if (hasConfig) {
            config = new Function(`return (${script.textContent})`)();
        }

        // if its not a configuration script, execute it
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        document.body.appendChild(newScript);
        document.body.removeChild(newScript);
    });

    return config;
}


async function router(path, params = null) {
    const route = routes.find(route => route.path === path) || "/html/404.html";

    const viewContainer = document.getElementById('router-view');
    const htmlContent = await fetch(PATH_TO_VIEWS + route.view).then(response => response.text());


    const viewConfigurations = handelViewScripts(htmlContent);
    console.log("viewConfigurations", viewConfigurations);

    // execute the before route hook if it exists
    viewConfigurations?.hooks?.beforeRouteEnter();
    const pathWithParams = params ? `${path}?${params}` : path;
    history.pushState({}, 'newUrl', pathWithParams);

    // execute the before dome inser hook if it exists
    viewConfigurations?.hooks?.beforeDomInsersion();
    viewContainer.innerHTML = htmlContent;
    // execute the after dome inser hook if it exists
    viewConfigurations?.hooks?.afterDomInsersion();
}
