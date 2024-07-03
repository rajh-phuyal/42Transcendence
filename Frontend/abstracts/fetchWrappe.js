
// BASE_URL = 'https://localhost:80';
BASE_URL = "https://random.dog"; // temporary

async function call(url, method, data) {

    const fullUrl = `${BASE_URL}${url}`;
    const payload = {
        mode: 'cors',
        cache: 'no-cache',
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        ...method !== 'GET' ? {
            body: JSON.stringify(data),
        } : {},
    };

    return await fetch(fullUrl, payload).then((response) => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response;
    })
}

async function callTheCall() {

    let test = "/woof.json";

    let waiter = call(test, 'GET', data);

    await waiter.then((data) => {
        console.log("Data", data);
    }).catch((error) => {
        console.log("Caught an error: ", error);
    });
}

callTheCall();