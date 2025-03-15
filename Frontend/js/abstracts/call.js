// abstract out the fetch api to make it easier to call the api
import { translate } from '../locale/locale.js';
import $callToast from './callToast.js';

async function call(url, method, data = null, showToast = true) {
    const fullUrl = `${window.location.origin}/api/${url}`;

    const headers = {
        'Content-Type': 'application/json'
    };

    let payload = {
        method: method,
        headers: headers,
        credentials: 'include',
        ...(data && method !== 'GET' && method !== 'DELETE') ? {
            body: JSON.stringify(data),
        } : {},
    };

    const response = await fetch(fullUrl, payload);
    if (!response.ok) {
        let errorMessage;

        try {
            const errorData = await response.json();
            errorMessage = errorData.message;
        } catch (e) {
            // If parsing the JSON fails, fall back to a generic message
            errorMessage = translate("global:call", "requestFailed");
        }

        if (!errorMessage)
            errorMessage = translate("global:call", "requestFailed");

        if (showToast) {
            $callToast("error", errorMessage)
        }

        throw new Error(errorMessage);
    }

    return await response.json();
}

export default call;