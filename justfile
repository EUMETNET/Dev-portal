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
    @just config-external-services

    @echo "\033[1mAll services are up and running\033[0m"

config-external-services:
    just configure-vault
    just configure-keycloak
    just configure-apisix

stop:
    docker-compose stop

remove:
    docker-compose down -v

@start-external-services:
    docker-compose up -d --build

@configure-vault:
    docker exec -e VAULT_SECRET_ENGINE=${VAULT_SECRET_ENGINE} -it vault sh /vault/config/setup.sh || { just remove; exit 1; }

@configure-keycloak:
    ./keycloak/config/setup.sh || { just remove; exit 1; }

@configure-apisix:
    ./apisix_conf/setup.sh || { just remove; exit 1; }