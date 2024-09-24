#!/bin/bash

# Export all variables from the configuration file
set -a
source "$(dirname "$0")/config/load_config.sh"
set +a

# Retrieve the token
TOKEN=$($(dirname "$0")/get_admin_token.sh | tail -n 1)

STATUS_CODE=$(curl -s -o response.txt -w "%{http_code}" -X PUT "$API_URL/admin/users/$KC_USER_UUID/disable" \
  -H "Authorization: Bearer $TOKEN")
RESPONSE=$(cat response.txt)
rm response.txt
echo -e "\nRESPOMSE STATUS CODE: $STATUS_CODE"
echo -e "\nRESPONSE MSG: $RESPONSE\n"