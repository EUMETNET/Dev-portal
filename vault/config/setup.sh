#!/bin/sh
export VAULT_ADDR='http://127.0.0.1:8200'

SE_NAME="apisix-dev"

if ! vault secrets list | grep -q "${SE_NAME}/"; then
  vault secrets enable -path="${SE_NAME}" -version=1 kv
fi

tee apisix-policy.hcl << EOF
path "kv/${SE_NAME}/consumer/*" {
    capabilities = ["read"]
}
EOF

vault policy write apisix-policy apisix-policy.hcl
#vault kv put apisix-dev/jack auth-key=value	
