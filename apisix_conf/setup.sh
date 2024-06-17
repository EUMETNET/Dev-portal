#!/bin/bash

APISIX_ADMIN_API_PORTS=9180,9280

# Assuming you have two instances running on ports 9180 and 9280
for port in ${APISIX_ADMIN_API_PORTS//,/ }
do
    curl -i -X PUT \
        -H 'X-API-KEY: your-api-key' \
        -d '{
            "uri": "http://vault:8200",
            "prefix": "'"$VAULT_SECRET_ENGINE"/consumers'",
            "token": "'"$VAULT_TOKEN"'"
        }' \
        "http://localhost:$port/apisix/admin/secrets/vault/dev"
done