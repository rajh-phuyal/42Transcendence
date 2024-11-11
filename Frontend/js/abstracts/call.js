// abstract out the fetch api to make it easier to call the api
import $auth from '../auth/authentication.js';
import { $id } from './dollars.js'

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
        // TODO maybe remove this toast I added it for debbuging
        let errorMessage;

        try {
            const errorData = await response.json();
            errorMessage = "Error: " + errorData.detail || 'Request failed';
        } catch (e) {
            // If parsing the JSON fails, fall back to a generic message
            errorMessage = 'Request failed';
        }

        const errorToast = $id('error-toast');
        const errorToastMsg = $id('error-toast-message');
        
        console.log("Error message:", errorMessage);
        if (!errorMessage)
            errorMessage = 'Request failed';
        errorToastMsg.textContent = errorMessage;


        new bootstrap.Toast(errorToast, { autohide: true, delay: 10000 }).show();
        throw new Error(errorMessage);
    }


    
    return await response.json();
}

export default call;