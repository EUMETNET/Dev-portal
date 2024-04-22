import { User } from "oidc-client-ts";

function getUser() {
    const key = `oidc.user:${window.REACT_APP_KEYCLOAK_URL}realms/${window.REACT_APP_KEYCLOAK_REALM}:${window.REACT_APP_KEYCLOAK_CLIENTID}`;
    const oidcStorage = sessionStorage.getItem(key)
    if (!oidcStorage) {
        return null;
    }

    return User.fromStorageString(oidcStorage);
}

async function httpRequest(path, options, retryCount = 0) {
    const user = getUser();
    const token = user?.access_token;

    const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    if (!token) {
        throw new Error('User is not logged in');
    }

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

        if (response.status === 401) {
            if (retryCount >= 3) {
              throw new Error('Unauthorized after 3 attempts');
            }
            return httpRequest(path, options, retryCount + 1);
        }
        return response
    } catch (error) {
        throw error;
    }
}

export async function getAPIKey(retryCount = 0) {
    const response = await httpRequest('/getapikey', { method: 'GET' });

    const data = await response.json();

    return { data, isError: !response.ok };
}

export async function deleteAPIKey() {
    const response =  await httpRequest('/apikey', { method: 'DELETE' });

    const data = await response.json();

    return { data, isError: !response.ok };
}