#!/bin/bash

# Default configuration file path
ENV_FILE="$(dirname "$0")/config/.local-env"

# Function to display usage
usage() {
  echo "Usage: $0 [-e <env_file>] [--env_file <env_file>]"
  exit 1
}

# Parse named arguments using getopts
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -e|--env_file)
      ENV_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" 1>&2
      usage
      ;;
  esac
done

# Debugging: Print the final env file path
echo -e "\nUsing configuration file from path: $ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
  echo "Env file not found: $ENV_FILE"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a