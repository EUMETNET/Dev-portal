#!/bin/bash

APISIX_ADMIN_API_PORTS=9180,9280

# Assuming you have two instances running on ports 9180 and 9280
for port in ${APISIX_ADMIN_API_PORTS//,/ }
do
    echo "Configuring Vault secrets engine for APISIX instance on port $port"
    response=$(curl -i -X PUT \
        -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
        -d '{
            "uri": "http://vault:8200",
            "prefix": "'"$VAULT_SECRET_ENGINE"/consumers'",
            "token": "'"$VAULT_TOKEN"'"
        }' \
        "http://localhost:$port/apisix/admin/secrets/vault/dev" 2>&1)
    
    #echo "Response from Vault configuration: $response"

    sleep 1

    echo "Creating consumer group for APISIX instance on port $port"
    response=$(curl -i -X PUT \
        -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
        -d '{
            "plugins": {
                "limit-count": {
                    "count": 100,
                    "time_window": 60
                }
            },
            "id": "EUMETNET_USER"
        }' \
        "http://localhost:$port/apisix/admin/consumer_groups" 2>&1)

done

# Create dummy route for each APISIX instance
# Dummy upstreams are found from /upstream directory
echo "Creating dummy routes for APISIX instances"
response=$(curl -i -X PUT \
    -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
    -d '{
        "id": "bar",
        "uri": "/bar",
        "vars": [
            "OR",
            [
                "http_apikey",
                "~~",
                ".+"
            ],
            [
                "arg_apikey",
                "~~",
                ".+"
            ]
        ],
        "plugins": {
            "limit-count": {
                "count": 10,
                "time_window": 60
            },
            "key-auth": {},
            "proxy-rewrite": {
                "uri": "/"
            }
        },
        "upstream" : {
            "type": "roundrobin",
            "nodes": {
            "web1:80":1
            },
            "scheme": "http"
        }
    }' \
    "http://localhost:9180/apisix/admin/routes" 2>&1)

response=$(curl -i -X PUT \
    -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
    -d '{
        "id": "foo",
        "uri": "/foo",
        "vars": [
            "OR",
            [
                "http_apikey",
                "~~",
                ".+"
            ],
            [
                "arg_apikey",
                "~~",
                ".+"
            ]
        ],
        "plugins": {
            "limit-count": {
                "count": 10,
                "time_window": 60
            },
            "key-auth": {},
            "proxy-rewrite": {
                "uri": "/"
            }
        },
        "upstream" : {
            "type": "roundrobin",
            "nodes": {
            "web2:80":1
            },
            "scheme": "http"
        }
    }' \
    "http://localhost:9280/apisix/admin/routes" 2>&1)
    
    #echo "Response from route creation: $response"
