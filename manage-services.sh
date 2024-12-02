#!/bin/bash

export ENV=""

# Global common variables
export VAULT_TOKEN="00000000-0000-0000-0000-000000000000"
export VAULT_SECRET_ENGINE="apisix-dev"
export KEYCLOAK_MASTER_ADMIN_USER="admin"
export KEYCLOAK_MASTER_ADMIN_PW="admin"
export REALM_NAME="test"

# Determine the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Add check to see if jq is installed
if ! command -v jq &> /dev/null
then
    echo "jq could not be found. Please install jq to continue."
    exit 1
fi

_load_env() {
    if [ "$ENV" = "dev" ]; then
        export $(grep -v '^#' "$SCRIPT_DIR/.env.dev" | xargs)
    elif [ "$ENV" = "test" ]; then
        export $(grep -v '^#' "$SCRIPT_DIR/.env.test" | xargs)
    else
        echo "Invalid environment: '$ENV'. Please provide a valid environment: dev or test"
        exit 1
    fi
}

# List available commands
show_help() {
    echo "Available commands:"
    echo "  up [env]    - Start services (default: dev). Possible values for [env]: dev, test"
    echo "  stop [env]  - Stop services (default: dev). Possible values for [env]: dev, test"
    echo "  remove [env]- Remove services (default: dev). Possible values for [env]: dev, test"
}

# Command to start services
up() {
    ENV=${1:-dev}
    echo "Starting up $ENV environment"
    _up
}

# Internal command to start services
_up() {
    _load_env
    _start_external_services 
    _config_external_services
    echo -e "\033[1mAll services are up and running\033[0m"
}

# Configure external services
_config_external_services() {
    _configure_vault
    _configure_keycloak
    _configure_apisix
}

# Stop services
stop() {
    ENV=${1:-dev}
    echo "Stopping $ENV environment"
    _stop
}

# Internal command to stop services
_stop() {
    _load_env
    docker compose --profile $ENV -p $ENV stop
}

# Remove services
remove() {
    ENV=${1:-dev}
    echo "Removing $ENV environment"
    _remove
}

# Internal command to remove services
_remove() {
    _load_env
    docker compose --profile $ENV -p $ENV down -v
}

# Start external services
_start_external_services() {
    docker compose --profile $ENV -p $ENV up -d --build
}

# Configure Vault
_configure_vault() {
    docker exec -e VAULT_SECRET_ENGINE=${VAULT_SECRET_ENGINE} -i vault-${ENV} sh /vault/config/setup.sh || { remove $ENV; exit 1; }
    docker exec -e VAULT_SECRET_ENGINE=${VAULT_SECRET_ENGINE} -i vault-2-${ENV} sh /vault/config/setup.sh || { remove $ENV; exit 1; }
}

# Configure Keycloak
_configure_keycloak() {
    "$SCRIPT_DIR/keycloak/config/setup.sh" || { remove $ENV; exit 1; }
}

# Configure APISIX
_configure_apisix() {
    export APISIX_ADMIN_API_PORTS="${APISIX_ADMIN_API_PORT},${APISIX2_ADMIN_API_PORT}"
    "$SCRIPT_DIR/apisix_conf/setup.sh" || { remove $ENV; exit 1; }
}

# Main script logic to handle command-line arguments
case "$1" in
    up)
        up $2
        ;;
    stop)
        stop $2
        ;;
    remove)
        remove $2
        ;;
    *)
        show_help
        ;;
esac