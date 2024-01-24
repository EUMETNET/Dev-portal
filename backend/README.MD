# Backend
This is the backend application for dev portal
default program runs in development mode.

these configurations should work with vault and keycloak that are inluded in docker files

configurations are in backend\src\main\resources\application-dev.yaml file
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