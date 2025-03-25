import { $id } from './dollars.js';

function setViewLoading(isLoading) {
    const loading = $id('view-loader');
    const view = $id('router-view');

    const display = {
        true: 'flex',
        false: 'none'
    };

    loading.style.display = display[isLoading];
    view.style.display = display[!isLoading];
}

function isViewLoading() {
    return $id('view-loader').style.display === 'flex';
}

export { setViewLoading, isViewLoading };