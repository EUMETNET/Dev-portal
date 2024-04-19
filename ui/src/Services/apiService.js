import { User, UserManager } from "oidc-client-ts";

function getUser() {
    const key = `oidc.user:${window.REACT_APP_KEYCLOAK_URL}realms/${window.REACT_APP_KEYCLOAK_REALM}:${window.REACT_APP_KEYCLOAK_CLIENTID}`;
    const oidcStorage = sessionStorage.getItem(key)
    if (!oidcStorage) {
        return null;
    }

    return User.fromStorageString(oidcStorage);
}

async function http_request(path, options) {
    const user = getUser();
    const token = user?.access_token;

    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    const baseURL = window.REACT_APP_BACKEND_URL;

    const url = path ? `${baseURL}${path}` : baseURL;

    const headers = {
        ...defaultHeaders,
        ...options.headers
    };

    const body = options.body ? JSON.stringify(options.body) : undefined;

    try {
        const response = await fetch(url, {
            method: options.method,
            headers,
            body
        });
        return response
    } catch (error) {
        console.log('here?')
        return error;
    }
}

export async function getAPIKey() {
    return await http_request('/getapikey', { method: 'GET' });
}

export async function deleteAPIKey() {
    return await http_request('/apikey', { method: 'DELETE' });
}