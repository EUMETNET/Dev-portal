#!/bin/sh
export VAULT_ADDR='http://127.0.0.1:8200'

vault secrets enable -path=apisix -version=1 kv

tee apisix-policy.hcl << EOF
path "kv/apisix/consumer/*" {
    capabilities = ["read"]
}
EOF

vault policy write apisix-policy apisix-policy.hcl
vault kv put apisix/jack auth-key=value	
