# Dev-portal
In Developer Portal authenticated user can create, check or delete API key. API key is used for access to FEMDI data via API Gateway. Authenticated user can also list all the available routes (= MET upstreams) in API Gateway.

## Structure
The Dev portal consists of two custom components (UI & backend) and a few external integrations:

* **UI**: This is the user interface of the Dev portal. It's responsible for presenting data to users and handling user interactions.

* **Backend**: This is the server-side part of the Dev portal. It handles communication with external services. The backend is built using Python FastAPI.

* [**Keycloak**](https://www.keycloak.org/): An open-source Identity and Access Management solution used in the Dev portal. It's used to enable third-party registration and authentication. This allows users to register and authenticate using their existing accounts from services like Google, GitHub, and Apple.

* [**Hashicorp Vault**](https://www.vaultproject.io/): This is a tool for securely storing and accessing secrets. In the Dev portal, it's used to store the user's API key.

* [**APISIX**](https://apisix.apache.org/): This is an open-source API gateway used in the Dev portal. It handles routing requests to the appropriate backend services, and provides features like authentication, rate limiting, etc.

## Usage

### Prerequisities

[Just](https://just.systems/man/en/) is used to run the external integrations.

#### Installing just

on MacOS you can install **just** e.g. with brew:
```bash
brew install just
```

on Linux: 
```bash
TODO
```

### Running external integrations

`justfile` contains list of commands, called recipes, that contains shell command(s).

To start the external integrations stack, run in project root directory:

```sh
just up
```

To stop the running containers:

```sh
just stop
```

To remove the containers:
```sh
just remove
```

### Run custom components
Refer the READMEs in [ui/](ui/) and [backend/](backend/) directories

### Playing around
Once external integrations, UI and backend are running:

1. Navigate to keycloak admin login page http://localhost:8080/ and login with
```
username: admin
password: admin
```
2. Change realm to "test" realm. You can change realm from the upper left corner's dropdown.

3. Create new user(s).
    1. Enter the general information (username, email etc.) 
    2. (Optional) you can also add user to group(s). By default each user is added to **USER** group but you can add user to **ADMIN** group. Admin group is needed if some administrative tasks needs to be tested/run with this user.
    3. When user is created add the credentials from "Credentials" tab within users -> User details page.

4. Setup IdP(s). In Keycloak UI found in left pane "Identity providers". By default Github and Google IdPs are enabled. However those needs to be configured to be able to use them. You can follow next link to setup Github OAuth app https://medium.com/keycloak/setting-up-keycloak-using-github-identity-provider-in-express-314e511a240b.
    1. in Github you need add the following values:
    ```
    Application name: keycloak-local-test-app
    Homepage URL: http://localhost:8080/realms/test
    Authorization callback URL: http://localhost:8080/realms/test/broker/github/endpoint
    ```
    2. Copy the generated Client ID and Client secret and replace corresponding values in Keycloak with them.

5. Login to dev portal (http://localhost:3002) with the created user or using the IdP. Now you can create new API key, delete it or list APISIX routes. 
