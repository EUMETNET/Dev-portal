# Dev-portal
In Developer Portal authenticated user can create, check or delete API key. API key is used for access to FEMDI data via API Gateway. Authenticated user can also list all the available routes (= MET upstreams) in API Gateway.

## Structure
The Dev portal consists of two custom components (UI & backend) and a few external integrations:

* **UI**: This is the user interface of the Dev portal. It's responsible for presenting data to users and handling user interactions.

* **Backend**: This is the server-side part of the Dev portal. It handles communication with external services. The backend is built using Python FastAPI.

* **user-sync-tool**: Tool for syncing the Dev-portal user information between a source and target Apisix and/or Vault instances. Built using Python poetry and httpx

* **Helm** Contains the Helm chart for installing the Dev-portal to a Kubernetes cluster. Only deploys UI and Backend

* [**Keycloak**](https://www.keycloak.org/): An open-source Identity and Access Management solution used in the Dev portal. It's used to enable third-party registration and authentication. This allows users to register and authenticate using their existing accounts from services like Google, GitHub, and Apple.

* [**Hashicorp Vault**](https://www.vaultproject.io/): This is a tool for securely storing and accessing secrets. In the Dev portal, it's used to store the user's API key.

* [**APISIX**](https://apisix.apache.org/): This is an open-source API gateway used in the Dev portal. It handles routing requests to the appropriate backend services, and provides features like authentication, rate limiting, etc.

## Usage

### Prerequisities

Docker Compose V2 is used to run the external integrations with profiles.

### Running external integrations

`manage-services.sh` contains list of commands that manage external integrations.

To initialize, configure, and start the external integrations, run in project root directory:

```sh
./manage-services.sh up
```

To stop the running containers:

```sh
./manage-services.sh stop
```

To remove the containers etc.:
```sh
./manage-services.sh remove
```

To manage external integrations for testing you should give "test" argument to command e.g. 
```sh
./manage-services.sh up test
```

### Run custom components
Refer the READMEs in [ui/](ui/) and [backend/](backend/) directories

### Verify everything works
Once external integrations, UI and backend are running:

1. **Keycloak**

    Admin login page should be accessible in http://localhost:8080/

    you can test login with credentials:
    ```
    username = admin
    password = admin
    ```

    You can check from the UI's upper left corner's dropdown that there is "test" realm created.

2. **Vault**

    There should be two Vault instances running.
    UIs should be accessible at http://localhost:8200 and http://localhost:8203
    
    you can login with:
    ```
    Method = Token
    Token = 00000000-0000-0000-0000-000000000000
    ```

    Click "Secret Engines" from the left side panel. There should be "apisix-dev/" kv engine created.

3. **Dev Portal Backend**

    Should be running in http://localhost:8082. You can test that e.g. with curl
    ```sh
    curl -X GET http://localhost:8082/health
    ```
4. **Dev Portal UI**

    Should be running in http://localhost:3002

    The `manage-users.sh up` command created three dummy users to Keycloak. You can check the users and credentials from `./keycloak/config/dummy-users.json`. For testing you can login with username & password:
    ```
    username = user
    password = user
    ```
    Once logged in to Dev Portal click Get API key and save it to somewhere. You can also check available routes and delete API key.

5. **APISIX**

    There should be two GW instances running at http://127.0.0.1:9080 and http://127.0.0.1:9181

    You can test that API key created in previous step works with GW instances.

    ```sh
    # API key given in header

    curl -X GET http://127.0.0.1:9080/bar -H "apikey: <your-api-key-here>"
    curl -X GET http://127.0.0.1:9181/foo -H "apikey: <your-api-key-here>"

    # API key in as query param

    curl -X GET http://127.0.0.1:9080/bar?apikey=<your-api-key-here>
    curl -X GET http://127.0.0.1:9181/foo?apikey=<your-api-key-here>

    # Response should be something like {"message": "Hello from dummy upstream server web1"}

    ```

6. **Optional**

    #### Setup Identity Providers (IdPs)
    To configure identity providers in Keycloak (within the "meteogate" realm):

    1. Navigate to "Identity Providers" in the left pane of the Keycloak UI. By default, GitHub and Google IdPs are enabled but require configuration to be functional. Follow e.g. [this guide](https://medium.com/keycloak/setting-up-keycloak-using-github-identity-provider-in-express-314e511a240b.) to set up a GitHub OAuth app.

    2. In GitHub, provide the following details:
    ```
    Application name: keycloak-local-test-app
    Homepage URL: http://localhost:8080/realms/meteogate
    Authorization callback URL: http://localhost:8080/realms/meteogate/broker/github/endpoint
    ```

    3. Copy the generated Client ID and Client Secret from GitHub and enter them into the corresponding fields in Keycloak.

### Users

There are three kind of users - users, eumetnet users and admin users. 

Every created user belongs to ***User*** group. By demand user can be promoted by admin to ***EumetnetUser*** group. Difference between these groups is that eumetnet users get better rate limits for the Gateway usage. Admin users can perform user related operations with Dev Portal backend - add/remove user from eumetnet user group, disable/enable user or delete user. Refer [backend/](backend/) to check admin related scripts.
