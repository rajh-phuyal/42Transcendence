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
        /*        ...(data && method !== 'GET' && method !== 'DELETE') ? {
            body: JSON.stringify(data),
            } : {}, */
        };

    // TODO: DONT DO THIS -> WILL TRIGGER RECURSION
    // Check if user is authenticated
    // import $auth from '../auth/authentication.js';
    //await $auth.isUserAuthenticated();

    // Add body only when appropriate
    if (data && method !== 'GET' && method !== 'DELETE') {
        payload.body = JSON.stringify(data);
    }

    let response;
    let jsonData = null;
    try {
        response = await fetch(fullUrl, payload);
        // Try to parse the JSON regardless of response.ok
        try {
            jsonData = await response.json();
        } catch (e) {
            jsonData = null;
        }

        if (!response.ok) {
            let errorMessage;
            errorMessage = jsonData?.message || translate("global:call", "requestFailed");
            if (showToast)
                $callToast("error", errorMessage)
            throw new Error(errorMessage);
        }
    } catch (error) {
        console.log("Error calling the API (doesn't need to be a bad thing...)");
        throw error;
    }
    if (jsonData === null) {
        if (showToast) {
            $callToast("error", translate("global:call", "badJson"));
        }
        throw new Error("Invalid JSON response");
    }
    return jsonData;
}

export default call;