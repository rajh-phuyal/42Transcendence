/* all the authentication logic is incapsulated here*/

class Auth {
    constructor() {
        this.jwtToken = localStorage.getItem('jwtToken');

        return this;
    }

    isAuthenticated = () => {
        return this.jwtToken !== null;
    }

    getAuthHeader() {
        return `Bearer ${this.jwtToken}`;
    }

    login(username, password) {
        // make a request to the server to authenticate the user
        this.jwtToken = token;
        localStorage.setItem('jwtToken', token);
    }

    logout() {
        this.jwtToken = null;
        localStorage.removeItem('jwtToken');
    }

    verifyJWTToken = () => {
        // check if the token is valid
        return true;
    }

    getJWTToken = () => {
        return this.jwtToken;
    }
}

export { Auth, doSomething };