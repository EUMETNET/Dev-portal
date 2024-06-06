#!/bin/bash

KEYCLOAK_URL="http://localhost:8080"
KEYCLOAK_USERNAME="admin"
KEYCLOAK_PASSWORD="admin"
REALM_CONFIG_FILE="./keycloak/config/realm_export/realm-export.json"
REALM_NAME="test"

echo "Waiting for Keycloak to be ready..."

# No easy way to do healthcheck in docker-compose, so we do it manually
# https://www.keycloak.org/server/health
counter=0
while : ; do 
  error=$(curl --output /dev/null --silent --head --fail http://localhost:8080/health/ready 2>&1)
  if [ $? -eq 0 ]; then
    break
  else
    sleep 5
    counter=$((counter+1))
    if [ $counter -ge 5 ]; then
      echo "Keycloak did not become healthy after 5 attempts. Exiting..."
      echo "Last error was: $error"
      exit 1
    fi
    echo "Keycloak not ready yet. Waiting 5 seconds before next check..."
  fi
done

# Obtain an access token for admin
TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${KEYCLOAK_USERNAME}" \
  -d "password=${KEYCLOAK_PASSWORD}" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r '.access_token')

# Check if the realm already exists
if curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${TOKEN}" "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}" | grep -q "200"; then
  echo "Realm ${REALM_NAME} already exists."
else
  # Create a new realm
  curl -s -X POST "${KEYCLOAK_URL}/admin/realms" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -d "@${REALM_CONFIG_FILE}"
  echo "Realm ${REALM_NAME} created."
fi

# Add more things e.g. creating some users if found helpful in future
