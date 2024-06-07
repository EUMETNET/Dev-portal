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