import { routes } from './routes.js';

function handelViewScripts(content) {
    const temp = document.createElement('div');
    temp.innerHTML = content;

    let config = null;
    const scripts = temp.querySelectorAll('script');

    scripts.forEach(script => {
        console.log(script.getAttribute('view-config'));
        const hasConfig = script.getAttribute('view-config') !== null;
        if (hasConfig) {
            document.body.appendChild(newScript);
            document.body.removeChild(newScript);
            config = new Function(`return (${script.textContent})`)();
        }

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
    const htmlContent = await fetch(`./${route.view}`).then(response => response.text());

    const viewConfigurations = handelViewScripts(htmlContent);

    viewConfigurations?.hooks?.beforeRouteEnter();
    const pathWithParams = params ? `${path}?${params}` : path;
    history.pushState({}, 'newUrl', pathWithParams);

    viewConfigurations?.hooks?.beforeDomInsersion();
    viewContainer.innerHTML = htmlContent;
    viewConfigurations?.hooks?.afterDomInsersion();
}

export { router };