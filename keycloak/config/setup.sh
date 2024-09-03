#!/bin/bash

echo "Waiting for Keycloak to be ready before checking Realm export..."

# No easy way to do healthcheck in docker-compose, so we do it manually
# https://www.keycloak.org/server/health
counter=0
while : ; do 
  error=$(curl --output /dev/null --silent --head --fail http://localhost:${KEYCLOAK_MNGT_PORT}/health/ready 2>&1)
  if [ $? -eq 0 ]; then
    echo "Keycloak is ready."
    break
  else
    sleep 5
    counter=$((counter+1))
    if [ $counter -ge 10 ]; then
      echo "Keycloak did not become healthy after 5 attempts. Exiting..."
      echo "Last error was: $error"
      exit 1
    fi
    echo "Keycloak not ready yet. Waiting 5 seconds before next check..."
  fi
done

# Obtain an access token for admin
echo "Requesting access token..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:${KEYCLOAK_PORT}/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${KEYCLOAK_MASTER_ADMIN_USER}" \
  -d "password=${KEYCLOAK_MASTER_ADMIN_PW}" \
  -d "grant_type=password" \
  -d "client_id=admin-cli")

echo "Token response: $TOKEN_RESPONSE"
TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

if [ -z "$TOKEN" ]; then
  echo "Failed to obtain access token. Exiting..."
  exit 1
fi

# Read dummy users
user_data=$(cat "./keycloak/config/dummy-users.json")

# Create users and assign them to groups
echo "${user_data}" | jq -c '.[]' | while read user; do

    username=$(echo $user | jq -r '.username')
    echo "Processing user: $username"

    # Check if the user already exists
    USER_EXISTS_RESPONSE=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users?username=${username}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${TOKEN}")

    echo "User exists response: $USER_EXISTS_RESPONSE"
    user_exists=$(echo $USER_EXISTS_RESPONSE | jq -r 'any(.[]; .username == "'"${username}"'")')

    # Create the user if it does not exist
    if [ "$user_exists" == "false" ]; then
      echo "Creating user: $username"
      CREATE_USER_RESPONSE=$(curl -s -X POST "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer ${TOKEN}" \
          -d "${user}")

      echo "Create user response: $CREATE_USER_RESPONSE"

      # Retrieve the user ID for non 'regular' users to add them to a group
      if [ "$username" != "user" ]; then
          USER_ID_RESPONSE=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users?username=${username}" \
              -H "Authorization: Bearer ${TOKEN}")

          echo "User ID response: $USER_ID_RESPONSE"
          user_id=$(echo $USER_ID_RESPONSE | jq -r '.[0].id')

          if [ "$username" == "better_user" ]; then
                  GROUP_NAME="EUMETNET_USER"
          elif [ "$username" == "realm_admin" ]; then
                  GROUP_NAME="ADMIN"
          fi

          # Retrieve the group ID
          GROUP_ID_RESPONSE=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/groups?search=${GROUP_NAME}" \
              -H "Authorization: Bearer ${TOKEN}")

          echo "Group ID response: $GROUP_ID_RESPONSE"
          group_id=$(echo $GROUP_ID_RESPONSE | jq -r '.[0].id')

          # Add the user to the group
          ADD_GROUP_RESPONSE=$(curl -s -X PUT "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users/${user_id}/groups/${group_id}" \
              -H "Authorization: Bearer ${TOKEN}" \
              -H "Content-Type: application/json" \
              -d '{}')

          echo "Add group response: $ADD_GROUP_RESPONSE"
      fi
    else
      echo "User $username already exists."
    fi
done