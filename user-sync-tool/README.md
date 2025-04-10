# user-sync-tool

User-sync-tool is a simple Python application for syncing dev-portal user data between target and source Vault and/or Apisix.
In practice user can provide Apisix parameters or Vault parameters and both or either ones are synced between the target ands source.

```bash
user-sync-tool
├── app
│   ├── config.py # Loads configurations
│   ├── constants.py # App wide constant
│   ├── dependencies # Dependencies needed in services
│   │   └── http_client.py
│   ├── exceptions.py # Exceptions types
│   ├── __init__.py # Make main a moduöe
│   ├── main.py # Entry point
│   ├── models # Pydantic data models for
│   │   ├── apisix.py
│   │   ├── __init__.py
│   │   ├── request.py
│   │   └── vault.py
│   └── services # Services. Makes the actual API-calls
│       ├── apisix.py
│       ├── __init__.py
│       ├── sync.py
│       └── vault.py
├── config.default.yaml
├── Dockerfile
├── poetry.lock
├── pyproject.toml
├── README.md
├── scripts # Scrits that Poetry runs
│   └── poetry.py
├── secrets.default.yaml
└── secrets.test.yaml

```

## Prerequisites

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
log_level: INFO
```

You can leave out `apisix`or `vault`keys depeding on if you want the vault or apisix instances to be synced with each other
#### Example secrets.default.yaml
```yaml
apisix:
  source_apisix:
    admin_url: http://127.0.0.1:9180
    admin_api_key: edd1c9f034335f136f87ad84b625c8f1
  target_apisix:
    admin_url: http://127.0.0.1:9280
    admin_api_key: edd1c9f034335f136f87ad84b625c8f1
vault:
  source_vault:
    url: http://127.0.0.1:8200
    token: 00000000-0000-0000-0000-000000000000
    base_path: apisix-dev/consumers
  target_vault:
    url: http://127.0.0.1:8203
    token: 00000000-0000-0000-0000-000000000000
    base_path: apisix-dev/consumers

```

### Run app in development mode
To run the application in local machine
```bash
poetry run python -m app.main
```

If for some reason you need to run the application with different config and/or secrets file you can do it by giving the file as env variable to start command
```bash
CONFIG_FILE=better-config.yaml SECRETS_FILE=super-secrets.yaml poetry run python -m app.main
```

You can also run the app in docker. Next one is pulling image from Github Container Registry. Replace `<sha-commit_tag>` with actual tag:
`--network="host"` will give the container access to localhost.
```bash
docker run --network="host" --platform=linux/amd64 ghcr.io/eumetnet/dev-portal/user-sync-tool:<sha-commit_tag>
```
To mount different secrets file to container
```bash
docker run --network="host" -v $(pwd)/your-super-secrets.yaml:/code/secrets.yaml --platform=linux/amd64 ghcr.io/eumetnet/dev-portal/user-sync-tool:<sha-commit_tag>
```

### Static analysis tools and tests

There are couple of analyze tools used. All the tool specific configurations if any are placed in pyproject.toml file.

1. [Black](https://pypi.org/project/black/) for checking and formatting code. You can run black formatting with `poetry run format` or to check if there is anything to format with `poetry run format-check`

2. [Pylint](https://pylint.readthedocs.io/en/latest/) for linting the application code. To run pylint type `poetry run lint`

3. [Mypy](https://www.mypy-lang.org/) for static type checking. Current rules are taken from https://careers.wolt.com/en/blog/tech/professional-grade-mypy-configuration. To run pylint type `poetry run type-check`

4. [Bandit](https://bandit.readthedocs.io/en/latest/) to find common security issues in Python code. To run bandit type `poetry run sec-check`

All of these are run also in ci cd pipeline before building the image.
