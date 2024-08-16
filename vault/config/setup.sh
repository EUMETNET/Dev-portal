#!/bin/sh
VAULT_ADDR='http://127.0.0.1:8200'

# Check Vault status
MAX_ATTEMPTS=5
ATTEMPT=1
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  vault status > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    break
  fi
  echo "Vault is not ready. Retrying again after 0.5 seconds..."
  ATTEMPT=$((ATTEMPT + 1))
  sleep 0.5
done

if ! vault secrets list | grep -q "${VAULT_SECRET_ENGINE}/"; then
  vault secrets enable -path="${VAULT_SECRET_ENGINE}" -version=1 kv
fi

tee apisix-policy.hcl << EOF
path "kv/${VAULT_SECRET_ENGINE}/consumers/*" {
    capabilities = ["read"]
}
EOF

vault policy write apisix-policy apisix-policy.hcl
