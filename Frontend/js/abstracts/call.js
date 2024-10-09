// abstract out the fetch api to make it easier to call the api
import $auth from '../auth/authentication.js';

async function call(url, method, data) {
    const fullUrl = `${window.location.origin}/api/${url}`;

    const headers = {
        'Content-Type': 'application/json'
    };

    if ($auth.getAuthHeader() && $auth.isUserAuthenticated()) {
        headers['Authorization'] = $auth.getAuthHeader();
    }

    let payload = {
        method: method,
        headers: headers,
        ...(method !== 'GET' && method !== 'DELETE') ? {
            body: JSON.stringify(data),
        } : {},
    };

    let response = await fetch(fullUrl, payload);

    if (!response.ok) {
        throw new Error(await response.json().detail || 'Request failed');
    }
    return await response.json();
}

export default call;