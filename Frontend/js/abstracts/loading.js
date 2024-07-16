import { $id } from './dollars.js';

function setViewLoading(isLoading) {
    const loading = $id('view-loader');
    const view = $id('router-view');

    const display = {
        true: 'block',
        false: 'none'
    };

    view.style.display = display[!isLoading];
    loading.style.display = display[isLoading];
}

export { setViewLoading };