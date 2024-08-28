#!/bin/bash

# Source the configuration file to export all variables
source "$(dirname "$0")/config/load_config.sh"

# Retrieve the token
TOKEN=$($(dirname "$0")/get_admin_token.sh)

STATUS_CODE=$(curl -s -o response.txt -w "%{http_code}" -X PUT "$API_URL/admin/users/$KC_USER_UUID/remove-group" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"groupName\": \"$KC_GROUP_NAME\"}")
RESPONSE=$(cat response.txt)
rm response.txt
echo -e "\nRESPOMSE STATUS CODE: $STATUS_CODE"
echo -e "\nRESPONSE MSG: $RESPONSE\n"