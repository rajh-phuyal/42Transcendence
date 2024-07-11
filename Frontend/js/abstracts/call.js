
// const BASE_URL = 'https://localhost:80';
const BASE_URL = "https://random.dog"; // temporary

async function call(url, method, data) {

    const fullUrl = `${BASE_URL}${url}`;
    let payload = {
        mode: 'no-cors',
        cache: 'no-cache',
        method: method,
        headers: {
            'Access-Control-Allow-Origin': '*', // temporary
            'Content-Type': 'application/json',
        },
        ...(method !== 'GET' && method !== 'DELETE') ? {
            body: JSON.stringify(data),
        } : {},
    };

    return await fetch(fullUrl, payload).then((res) => {
        console.log("first callback called!");
        return res;
    });
    // return await fetch(fullUrl, payload).then((res) => {
    //     console.log("first callback called!");
    //     return res;
    // });
}


export { call };