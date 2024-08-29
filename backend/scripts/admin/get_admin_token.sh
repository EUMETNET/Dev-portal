#!/bin/bash

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed." >&2
  exit 1
fi

# Function to get the token
TOKEN=$(curl -s -X POST "$KC_URL/realms/$KC_REALM/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$KC_USERNAME" \
  -d "password=$KC_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=$KC_CLIENT_ID" | jq -r '.access_token')

if [ -z "$TOKEN" ]; then
  echo "Error: Failed to retrieve token" >&2
  exit 1
fi

echo "$TOKEN"
