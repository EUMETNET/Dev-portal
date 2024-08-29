#!/bin/sh
VAULT_ADDR='http://127.0.0.1:8200'

if ! vault secrets list | grep -q "${VAULT_SECRET_ENGINE}/"; then
  vault secrets enable -path="${VAULT_SECRET_ENGINE}" -version=1 kv || exit 1
fi

tee apisix-policy.hcl << EOF
path "kv/${VAULT_SECRET_ENGINE}/consumers/*" {
    capabilities = ["read"]
}
EOF

vault policy write apisix-policy apisix-policy.hcl
