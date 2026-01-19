#!/bin/bash

# Test script to demonstrate the new unified API behavior
# This script shows how the HTTP API now matches the CLI command structure

echo "=== Fark HTTP API Test Script ==="
echo

# Note: This requires fark server to be running and a connected Kubernetes cluster
# Start server with: ./fark server

BASE_URL="http://localhost:8080"

echo "1. Testing GET endpoints (list resources like CLI without arguments):"
echo

echo "GET /agents (equivalent to 'fark agent'):"
curl -s -X GET "$BASE_URL/agents" | jq -r '. | length' 2>/dev/null && echo " agents found" || echo "Request failed or no jq installed"
echo

echo "GET /teams (equivalent to 'fark team'):"
curl -s -X GET "$BASE_URL/teams" | jq -r '. | length' 2>/dev/null && echo " teams found" || echo "Request failed or no jq installed"
echo

echo "GET /models (equivalent to 'fark model'):"
curl -s -X GET "$BASE_URL/models" | jq -r '. | length' 2>/dev/null && echo " models found" || echo "Request failed or no jq installed"
echo

echo "GET /tools (equivalent to 'fark tool'):"
curl -s -X GET "$BASE_URL/tools" | jq -r '. | length' 2>/dev/null && echo " tools found" || echo "Request failed or no jq installed"
echo

echo "GET /queries (equivalent to 'fark query'):"
curl -s -X GET "$BASE_URL/queries" | jq -r '. | length' 2>/dev/null && echo " queries found" || echo "Request failed or no jq installed"
echo

echo "2. Testing POST endpoints (query specific resources by name in path):"
echo

echo "POST /agent/my-agent (equivalent to 'fark agent my-agent \"Hello world\"'):"
echo "curl -X POST $BASE_URL/agent/my-agent -H 'Content-Type: application/json' -d '{\"input\":\"Hello world\"}'"
echo

echo "POST /team/my-team (equivalent to 'fark team my-team \"Analyze data\"'):"
echo "curl -X POST $BASE_URL/team/my-team -H 'Content-Type: application/json' -d '{\"input\":\"Analyze data\"}'"
echo

echo "POST /model/my-model (equivalent to 'fark model my-model \"What is 2+2?\"'):"
echo "curl -X POST $BASE_URL/model/my-model -H 'Content-Type: application/json' -d '{\"input\":\"What is 2+2?\"}'"
echo

echo "POST /tool/my-tool (equivalent to 'fark tool my-tool \"Execute task\"'):"
echo "curl -X POST $BASE_URL/tool/my-tool -H 'Content-Type: application/json' -d '{\"input\":\"Execute task\"}'"
echo

echo "POST /query/my-query (equivalent to 'fark query my-query \"New input\"'):"
echo "curl -X POST $BASE_URL/query/my-query -H 'Content-Type: application/json' -d '{\"inputOverride\":\"New input\"}'"
echo

echo "=== Clean API Structure ==="
echo "The HTTP API structure:"
echo "- GET /{resources} = fark {resource}                     (list all)"
echo "- POST /{resource}/{name} = fark {resource} <name> <input>  (query specific)"
echo "- POST /query/{name} = fark query <name> [overrides]     (trigger existing)"
echo
echo "Examples:"
echo "- GET /agents = list all agents"
echo "- POST /agent/my-agent = query specific agent named 'my-agent'"
echo "- POST /query/my-query = trigger specific query named 'my-query'"
echo
echo "✓ RESTful design with resource names in URL paths"
echo "✓ Separation of listing and querying operations"
echo "✓ Clear and intuitive API structure"