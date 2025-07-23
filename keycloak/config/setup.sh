#!/bin/bash

# Determine the directory where the script is located
SCRIPT_DIR=$(dirname "$(realpath "$0")")

echo "Waiting for Keycloak to be ready before configuring it..."

# No easy way to do healthcheck in docker-compose, so we do it manually
# https://www.keycloak.org/server/health
counter=0
while : ; do 
  error=$(curl --output /dev/null --silent --head --fail http://localhost:${KEYCLOAK_MNGT_PORT}/health/ready 2>&1)
  if [ $? -eq 0 ]; then
    break
  else
    sleep 5
    counter=$((counter+1))
    if [ $counter -ge 10 ]; then
      echo "Keycloak did not become healthy after 10 attempts. Exiting..."
      echo "Last error was: $error"
      exit 1
    fi
    echo "Keycloak not ready yet. Waiting 5 seconds before next check..."
  fi
done

if [ "$ENV" = "dev" ]; then
  # Obtain an access token for admin
  TOKEN=$(curl -s -X POST "http://localhost:${KEYCLOAK_PORT}/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${KEYCLOAK_MASTER_ADMIN_USER}" \
    -d "password=${KEYCLOAK_MASTER_ADMIN_PW}" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

  # Read dummy users
  user_data=$(cat "$SCRIPT_DIR/dummy-users.json")

  # Create users and assing them to groups
  echo "${user_data}" | jq -c '.[]' | while read user; do

      username=$(echo $user | jq -r '.username')

      # Check if the user already exists
      user_exists=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users?username=${username}" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer ${TOKEN}" | jq -r 'any(.[]; .username == "'"${username}"'")')

      # Create the user if it does not exist
      if [ "$user_exists" == "false" ]; then
        curl -s -X POST "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${TOKEN}" \
            -d "${user}"

        # Retrieve the user ID for non 'regular' users to add them to a group
        if [ "$username" != "user" ]; then
            user_id=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users?username=${username}" \
                -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')
            if [ "$username" == "better_user" ]; then
                    GROUP_NAME="EumetnetUser"
            elif [ "$username" == "realm_admin" ]; then
                    GROUP_NAME="Admin"
            fi

            # Retrieve the group ID
            group_id=$(curl -s -X GET "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/groups?search=${GROUP_NAME}" \
                -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')

            # Add the user to the group
            curl -s -X PUT "http://localhost:${KEYCLOAK_PORT}/admin/realms/${REALM_NAME}/users/${user_id}/groups/${group_id}" \
                -H "Authorization: Bearer ${TOKEN}" \
                -H "Content-Type: application/json" \
                -d '{}'
        fi
      fi
  done
fi