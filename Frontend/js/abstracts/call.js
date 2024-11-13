// abstract out the fetch api to make it easier to call the api
import $auth from '../auth/authentication.js';
import { $id } from './dollars.js'
import $callToast from './callToast.js';

async function call(url, method, data) {
    // TODO: WHY IS THERE API IN THE URL? [astein is asking :D]
	const fullUrl = `${window.location.origin}/api/${url}`;

    const headers = {
        'Content-Type': 'application/json'
    };

    if ($auth.getAuthHeader() && await $auth.isUserAuthenticated()) {
        headers['Authorization'] = $auth.getAuthHeader();
    }

    let payload = {
        method: method,
        headers: headers,
        // TODO why (method !== 'GET' && method !== 'DELETE')?? @rajh
        ...(url == "user/relationship/" || (method !== 'GET' && method !== 'DELETE')) ? {
            body: JSON.stringify(data),
        } : {},
    };
    const response = await fetch(fullUrl, payload);
    
    if (!response.ok) {
        // TODO maybe remove this toast I added it for debbuging
        let errorMessage;

        try {
            const errorData = await response.json();
            
            if (errorData.error)
                errorMessage = "Error: " + errorData.error;
            else if (errorData.detail)
                errorMessage = "Error: " + errorData.detail;
            else
                errorMessage = 'Request failed';
        } catch (e) {
            // If parsing the JSON fails, fall back to a generic message
            errorMessage = 'Request failed';
        }
        
        if (!errorMessage)
            errorMessage = 'Request failed';

        $callToast("error", errorMessage)

        throw new Error(errorMessage);
    }


    
    return await response.json();
}

export default call;