#!/bin/bash

# Function to check the response status
check_response() {
    local response="$1"
    local port="$2"
    local status_code=$(echo "$response" | grep HTTP | awk '{print $2}')
    if [ -z "$status_code" ]; then
        echo "Request failed for admin API on port $port with error: $response"
        exit 1
    elif [ "$status_code" -ne 200 ] && [ "$status_code" -ne 201 ]; then
        echo "Request failed for admin API on port $port with status code $status_code"
        exit 1
    fi
}

# Assuming you have two instances running on ports 9180 and 9280
echo "Configuring Vault secrets engine and consumer groups for APISIX instances"
for port in ${APISIX_ADMIN_API_PORTS//,/ }
do
    response=$(curl -i -X PUT \
        -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
        -d '{
            "uri": "http://vault:8200",
            "prefix": "'"$VAULT_SECRET_ENGINE"/consumers'",
            "token": "'"$VAULT_TOKEN"'"
        }' \
        "http://localhost:$port/apisix/admin/secrets/vault/dev" 2>&1)

    check_response "$response" "$port"

    response=$(curl -i -X PUT \
        -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
        -d '{
            "plugins": {},
            "id": "User"
        }' \
        "http://localhost:$port/apisix/admin/consumer_groups" 2>&1)

    check_response "$response" "$port"

    response=$(curl -i -X PUT \
        -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
        -d '{
            "plugins": {
                "limit-count": {
                    "count": 100,
                    "time_window": 60,
                    "key": "consumer_name"
                }
            },
            "id": "EumetnetUser"
        }' \
        "http://localhost:$port/apisix/admin/consumer_groups" 2>&1)

    check_response "$response" "$port"

done

# Create dummy route for each APISIX instance when running in dev mode
# Dummy upstreams are found from /upstream directory
if [ "$ENV" = "dev" ]; then
    echo "Creating dummy routes for APISIX instances"
    for port in ${APISIX_ADMIN_API_PORTS//,/ }
    do
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
                    "key-auth": {},
                    "limit-req": {
                        "rate": 10,
                        "burst": 20,
                        "key": "consumer_name",
                        "rejected_code": 429
                    },
                    "limit-count": {
                        "count": 10,
                        "time_window": 60,
                        "key": "consumer_name",
                        "rejected_code": 429
                    },
                    "proxy-rewrite": {
                        "regex_uri": ["^/bar(.*)", "/$1"]
                    }
                },
                "upstream": {
                    "type": "roundrobin",
                    "nodes": {
                        "web1:80": 1
                    },
                    "scheme": "http"
                }
            }' \
            "http://localhost:$port/apisix/admin/routes" 2>&1)

        check_response "$response" "$port"

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
                    "key-auth": {},
                    "limit-req": {
                        "rate": 5,
                        "burst": 10,
                        "key": "consumer_name",
                        "rejected_code": 429
                    },
                    "limit-count": {
                        "count": 5,
                        "time_window": 60,
                        "key": "consumer_name",
                        "rejected_code": 429
                    },
                    "proxy-rewrite": {
                        "regex_uri": ["^/foo(.*)", "/$1"]
                    }
                },
                "upstream": {
                    "type": "roundrobin",
                    "nodes": {
                        "web2:80": 1
                    },
                    "scheme": "http"
                }
            }' \
            "http://localhost:$port/apisix/admin/routes" 2>&1)

        check_response "$response" "$port"

        response=$(curl -i -X PUT \
            -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
            -d '{
                "id": "baz",
                "uri": "/baz",
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
                    "proxy-rewrite": {
                        "regex_uri": ["^/baz(.*)", "/$1"]
                    }
                },
                "upstream": {
                    "type": "roundrobin",
                    "nodes": {
                        "web1:80": 1
                    },
                    "scheme": "http"
                }
            }' \
            "http://localhost:$port/apisix/admin/routes" 2>&1)

        check_response "$response" "$port"

        response=$(curl -i -X PUT \
            -H 'X-API-KEY: edd1c9f034335f136f87ad84b625c8f1' \
            -d '{
                "id": "qux",
                "uri": "/qux",
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
                    "key-auth": {},
                    "proxy-rewrite": {
                        "regex_uri": ["^/qux(.*)", "/$1"]
                    }
                },
                "upstream": {
                    "type": "roundrobin",
                    "nodes": {
                        "web1:80": 1
                    },
                    "scheme": "http"
                }
            }' \
            "http://localhost:$port/apisix/admin/routes" 2>&1)

        check_response "$response" "$port"
    done
fi