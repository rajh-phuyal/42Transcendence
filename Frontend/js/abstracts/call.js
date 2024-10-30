// abstract out the fetch api to make it easier to call the api
import $auth from '../auth/authentication.js';

async function call(url, method, data) {
    // TODO: WHY IS THERE API IN THE URL? [astein is asking :D]
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
	console.log("Full URL: ", fullUrl);
    const response = await fetch(fullUrl, payload);

    if (!response.ok) {
        throw new Error(await response.json().detail || 'Request failed');
    }

    return await response.json();
}

export default call;