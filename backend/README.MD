# Backend
Backend application for Developer Portal written in Python 3.12 and FastAPI.

### Project structure
```bash
backend
├── app
│   ├── __init__.py  # Init module
│   ├── config.py # Configuration settings, logger etc
│   ├── constants.py # App wide constants
│   ├── dependencies # Dependencies needed in routers
│   │   ├── http_client.py
│   │   └── ...
│   ├── exceptions.py # Global exceptions
│   ├── main.py # Application runner
│   ├── routers # Routers (or controllers, routes) for the app
│   │   ├── __init__.py
│   │   ├── apikey.py
│   │   ├── ...
│   ├── services # Business logic & external services
│   │   ├── apisix.py
│   │   └── ...
│   └── utils # Utility functions and classes
│       ├── uuid.py
│       └── ...
├── tests
│    ├── conftest.py
│    └── ...
├── config.default.yaml # configuration values
├── secrets.default.yaml # secret values
├── scripts.py # scripts to run with poetry run
└── pyproject.toml # Configuration file for Poetry, dependencies, other metadata
```
### Prerequisites

1. Install Python version 3.12
2. Install [Poetry](https://python-poetry.org) 


### Initialize

To initialize the project, follow these steps:

1. Install the dependencies:
```bash
poetry install
```


### Configurations
By default the application looks for config file in path `backend/config.default.yaml` and secrets file in path `backend/secrets.default.yaml` 
For any reason you can override one or both of config and secrets settings. For example to override config create a file called `backend/config.yaml` or use an environment variable `CONFIG_FILE` for example `CONFIG_FILE=better-config.yaml`
`CONFIG_FILE` takes priority over the file paths.

#### Example config.default.yaml
```yaml
server:
  host: 0.0.0.0
  port: 8082
  log_level: "DEBUG"
  allowed_origins: ["*"]
```

#### Example secrets.default.yaml
```yaml
vault:
  base_path: apisix-dev/consumers
  secret_phase: geeks
  instances:
    - name: "EWC"
      token: 00000000-0000-0000-0000-000000000000
      url: http://127.0.0.1:8200
    - name: "ECMWF"
      token: 00000000-0000-0000-0000-000000000000
      url: http://127.0.0.1:8203

apisix:
  key_path: $secret://vault/dev/
  instances:
    - name : "EWC"
      admin_url: http://127.0.0.1:9180
      gateway_url: http://127.0.0.1:9080
      admin_api_key: edd1c9f034335f136f87ad84b625c8f1
    - name : "AWS"
      admin_url: http://127.0.0.1:9280
      gateway_url: http://127.0.0.1:9180
      admin_api_key: edd1c9f034335f136f87ad84b625c8f1

keycloak:
  url: http://127.0.0.1:8080
  realm: test
  client_id: dev-portal-api
  client_secret: okXCanJb0qrDPh54Le40eecLLvEh86Xw
```

### Run app in development mode
To run the application in local machine
```bash
poetry run start-dev
```

If for some reason you need to run the application with different config and/or secrets file you can do it by giving the file as env variable to start command
```bash
CONFIG_FILE=better-config.yaml SECRETS_FILE=super-secrets.yaml poetry run start-dev
```

You can also run the app in docker. Next one is pulling image from Github Container Registry. Replace `<sha-commit_tag>` with actual tag:
```bash
docker run --network dev-portal_apisix -p 8082:8082 --platform=linux/amd64 ghcr.io/eurodeo/dev-portal/backend:<sha-commit_tag>
```
To mount different secrets file to container
```bash
docker run --network dev-portal_apisix -p 8082:8082 -v $(pwd)/your-super-secrets.yaml:/code/secrets.yaml --platform=linux/amd64 ghcr.io/eurodeo/dev-portal/backend:<sha-commit_tag>
```

### Static analysis tools and tests

There are couple of analyze tools used. All the tool specific configurations if any are placed in pyproject.toml file.

1. [Black](https://pypi.org/project/black/) for checking and formatting code. You can run black formatting with `poetry run format` or to check if there is anything to format with `poetry run format-check`

2. [Pylint](https://pylint.readthedocs.io/en/latest/) for linting the application code. To run pylint type `poetry run lint`

3. [Mypy](https://www.mypy-lang.org/) for static type checking. Current rules are taken from https://careers.wolt.com/en/blog/tech/professional-grade-mypy-configuration. To run pylint type `poetry run type-check`

4. [Bandit](https://bandit.readthedocs.io/en/latest/) to find common security issues in Python code. To run bandit type `poetry run sec-check`

5. [Pytest](https://docs.pytest.org/en/8.0.x/index.html) to run tests. Before running tests make sure that external services stack for testing is up and running by running `/.manage-services up test` in repo's root directory and then run tests with `poetry run test`. Tests will default to use `secrets.test.yaml` file if no other is given.

All of these are run also in ci cd pipeline before building the image.

TODO add pre-commit hooks to automatically run these before commit

### Admin operations

There are few scripts that admin user can use to perform actions for a user. Scripts are found `scripts/admin/`. Example usage:
```sh
# You can export the user's Keycloak UUID or place it in an env file
export KC_USER_UUID=<some-uuid-here>

# By default the scripts will use the .local-env file for variables
./scripts/admin/update_user_to_group.sh

# You can specify different env file than the default
./scripts/admin/update_user_to_group.sh -e ./scripts/admin/config/.env
```

With scripts admin can:
  1. Disable(=ban) or enable user
    * When disabling user it will delete user's API if exists from APISIX instances and Vault
    * Enabling user does NOT create API key for one
  2. Add or remove user from group
    * By default each user belongs to USER group.
    * If promoting/removing user from EUMETNET_USER group the user's existing API key is also promoted/removed from the EUMETNET_USER group in APISIX instances. **NOTE: group names are case sensitive**
  3. Delete user will delete user from Keycloak and existing API key from Vault and APISIX instances
