# Define variables needed in multiple places
## VAULT
export VAULT_TOKEN := "00000000-0000-0000-0000-000000000000"
export VAULT_SECRET_ENGINE := "apisix-dev"
## KEYCLOAK
export KEYCLOAK_MASTER_ADMIN_USER := "admin"
export KEYCLOAK_MASTER_ADMIN_PW := "admin"

# list recipes
default:
    @just --list

up:
    just start-external-services
    just setup-vault
    just setup-keycloak
    just setup-apisix

    @echo "\033[1mAll services are up and running\033[0m"

stop:
    docker-compose stop

remove:
    docker-compose down -v

@start-external-services:
    docker-compose up -d

@setup-vault:
    docker exec -e VAULT_SECRET_ENGINE=${VAULT_SECRET_ENGINE} -it vault sh /vault/config/setup.sh 

@setup-keycloak:
    ./keycloak/config/setup.sh

@setup-apisix:
    ./apisix_conf/setup.sh