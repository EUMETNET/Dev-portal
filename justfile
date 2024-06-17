# Define variables needed in multiple places
export VAULT_TOKEN := "00000000-0000-0000-0000-000000000000"
export VAULT_SECRET_ENGINE := "apisix-dev"
export KEYCLOAK_MASTER_ADMIN_USER := "admin"
export KEYCLOAK_MASTER_ADMIN_PW := "admin"

# list recipes
default:
    @just --list

up:
    just start-external-services
    just setup-vault
    just setup-keycloak

stop:
    docker-compose stop

down:
    docker-compose down

start-external-services:
    docker-compose up -d

setup-vault:
    docker exec -it vault_test sh /vault/config/setup.sh

setup-keycloak:
    ./keycloak/config/setup.sh

# setup-apisix:
#     do the needed configurations based on IaC
#     either implement ./apisix_conf/setup.sh
#     or modify config.yaml