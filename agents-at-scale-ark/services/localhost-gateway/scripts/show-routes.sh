#!/usr/bin/env bash

# Show available Gateway routes for localhost-gateway

set -e -o pipefail

# Colors for output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[1;33m'
white='\033[1;37m'
blue='\033[0;34m'
purple='\033[0;35m'
grey='\033[0;37m'
nc='\033[0m'

# Default values
NAMESPACE="${NAMESPACE:-ark-system}"
PORT="${PORT:-8080}"

# Set port suffix - empty for port 80, show port for others
if [ "$PORT" = "80" ]; then
    PORT_SUFFIX=""
else
    PORT_SUFFIX=":${PORT}"
fi

# Determine if sudo is needed for privileged ports
SUDO_CMD=""
if [ "$PORT" -lt 1024 ]; then
    SUDO_CMD="sudo "
fi

# Check if localhost-gateway is installed
if ! kubectl get gateway localhost-gateway -n "${NAMESPACE}" >/dev/null 2>&1; then
    echo -e "${red}error:${nc} localhost-gateway not installed in namespace '${NAMESPACE}'."
    echo -e "${blue}info:${nc} Run 'make install' first."
    exit 1
fi

# Get HTTPRoutes and count them
route_output=$(kubectl get httproutes -A -o custom-columns="NAMESPACE:.metadata.namespace,NAME:.metadata.name,HOSTNAMES:.spec.hostnames" --no-headers 2>/dev/null | sed 's/\[//g; s/\]//g; s/,//g')

if [[ -z "$route_output" ]]; then
    echo -e "${white}Available Localhost Gateway routes: 0${nc}"
    echo -e "${blue}info:${nc} No HTTPRoutes found. Install services to see routes here."
    exit 0
fi

# Count total routes by counting hostnames
route_count=$(echo "$route_output" | awk '{for(i=3; i<=NF; i++) if($i != "" && $i != "<none>") count++} END {print count+0}')

echo -e "${white}Available Localhost Gateway routes: ${route_count}${nc}"

# Check port-forward status
PORT_FORWARD_ACTIVE=false
if pgrep -f "kubectl.*port-forward.*${PORT}:80" >/dev/null 2>&1; then
    echo -e "${blue}info:${nc} Port-forward active on localhost${PORT_SUFFIX}"
    PORT_FORWARD_ACTIVE=true
else
    echo -e "${red}error:${nc} Port-forward not running on localhost${PORT_SUFFIX} - routes are not exposed"
    if [ "$PORT" -lt 1024 ]; then
        echo -e "${blue}run:${nc} ${SUDO_CMD}kubectl port-forward -n ${NAMESPACE} service/localhost-gateway-nginx ${PORT}:80 &"
        echo -e "${blue}note:${nc} Privileged port requires interactive terminal for sudo prompt"
    else
        echo -e "${blue}run:${nc} ${SUDO_CMD}kubectl port-forward -n ${NAMESPACE} service/localhost-gateway-nginx ${PORT}:80 > /dev/null 2>&1 &"
    fi
fi
echo ""

# Display the routes with proper alignment
# First pass: calculate maximum route name length
max_length=$(echo "$route_output" | awk '
{
    if($3 != "<none>" && $3 != "") {
        if(length($2) > max_len) max_len = length($2)
    }
} END { print max_len+0 }')

# Second pass: display with proper alignment using HTTPRoute names
echo "$route_output" | awk -v port_suffix="$PORT_SUFFIX" -v blue="$blue" -v red="$red" -v nc="$nc" -v max_len="$max_length" -v pf_active="$PORT_FORWARD_ACTIVE" '
{
    if($3 != "<none>" && $3 != "") {
        for(i=3; i<=NF; i++) {
            if($i != "") {
                if(pf_active == "true") {
                    printf "  %-*s: " blue "http://%s%s/" nc "\n", max_len, $2, $i, port_suffix
                } else {
                    printf "  %-*s: " blue "http://%s%s/" nc " " red "(unavailable)" nc "\n", max_len, $2, $i, port_suffix
                }
            }
        }
    }
}'