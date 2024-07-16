// abstract out the fetch api to make it easier to call the api

async function call(url, method, data) {
    const BASE_URL = "http://localhost:8000"; // backend django server

    const fullUrl = `${BASE_URL}${url}`;

    console.log("in the call function:", data);
    return ;
    let payload = {
        mode: 'no-cors', // temporary
        cache: 'no-cache',
        method: method,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
        ...(method !== 'GET' && method !== 'DELETE') ? {
            body: JSON.stringify(data),
        } : {},
    };

    return await fetch(fullUrl, payload).then((res) => {
        return res;
    });
}

export default call;