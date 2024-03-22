# Backend
Backend application for Developer Portal written in Python 3.12 and FastAPI.

### Project structure
```bash
backend
├── app
│   ├── __init__.py  # Init module
│   ├── config.py
│   ├── dependencies # Contains dependencies needed in routers
│   │   ├── http_client.py
│   │   └── ...
│   ├── exceptions.py # Custom exceptions
│   ├── main.py # init app 
│   ├── routers # Contains the routers (or controllers) for the app
│   │   ├── __init__.py
│   │   ├── apikey.py
│   │   ├── ...
│   ├── services # Contains the business logic & external services
│   │   ├── apisix.py
│   │   └── ...
│   └── utils # Utility functions and classes
│       ├── uuid.py
│       └── ...
├── tests
│    ├── conftest.py
│    └── ...
├── config.yaml # config values
└── pyproject.toml # Configuration file for Poetry, dependencies, other metadata
```
### Prerequisites

1. Install Python version 3.12
2. Install [Poetry](https://python-poetry.org) 


### Initialize

To initialize the project, follow these steps:

1. Install the dependencies: `poetry install`


### Configurations
By default the application looks for config file in path `backend/config.yaml`. The default config can be overrided with TODO

#### Example config.yaml
```sh
server:
  port: 8082

keycloak:
  url: http://localhost:8080
  realm: test

vault:
  endpoint: 127.0.0.1
  scheme: http
  port: 8200
  token: 00000000-0000-0000-0000-000000000000

apisix:
  consumersUrl: http://127.0.0.1:9180/apisix/admin/consumers
  adminApiKey: edd1c9f034335f136f87ad84b625c8f1
  keyPath: $secret://vault/1/
  keyName: api-key
```

### Run app in development mode

