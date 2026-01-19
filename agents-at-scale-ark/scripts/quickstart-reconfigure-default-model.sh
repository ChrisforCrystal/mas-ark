#!/usr/bin/env bash

set -e -o pipefail

# Colors for output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[1;33m'
white='\033[1;37m'
blue='\033[0;34m'
purple='\033[0;35m'
nc='\033[0m'

if [ -e .ark.env ]
then
	source .ark.env
fi

# Use environment variables if set, otherwise prompt
model_type=${ARK_QUICKSTART_MODEL_TYPE:-}
if [ -z "$model_type" ]; then
    read -p "model type (azure/openai) [default: azure]: " model_type
fi
model_type=${model_type:-azure}

# Use environment variables if set, otherwise prompt
model_version=${ARK_QUICKSTART_MODEL_VERSION:-}
if [ -z "$model_version" ]; then
    read -p "model version [default: gpt-4.1-mini]: " model_version
fi
model_version=${model_version:-"gpt-4.1-mini"}

base_url=${ARK_QUICKSTART_BASE_URL:-}
if [ -z "$base_url" ]; then
    read -p "enter your base URL: " base_url
fi
# Remove trailing slash from base URL (if any)
base_url=$(echo "$base_url" | sed 's:/*$::')

# Ask for API version only if Azure
if [ "$model_type" = "azure" ]; then
    API_VERSION=${ARK_QUICKSTART_API_VERSION:-}
    if [ -z "$API_VERSION" ]; then
        read -p "enter Azure API version [default: 2024-12-01-preview]: " api_version
        API_VERSION=${api_version:-2024-12-01-preview}
    fi
else
    API_VERSION=""
fi

api_key=${ARK_QUICKSTART_API_KEY:-}
if [ -z "$api_key" ]; then
    read -s -n 2000 -p "enter your API key: "   api_key
    echo
fi
# Convert to base64 without line wrapping or spaces
api_key=$(echo -n "$api_key" | base64 | tr -d '\n' | tr -d ' ')

kubectl patch secret azure-openai-secret -p '{"data":{"token":"'$api_key'"}}'
API_KEY="$api_key" BASE_URL="$base_url" MODEL_TYPE="$model_type" MODEL_VERSION="$model_version" API_VERSION="$API_VERSION" envsubst < samples/quickstart/default-model.yaml | kubectl apply -f -

echo -e "${green}✔${nc} default model is re-configured with fresh credentials"
