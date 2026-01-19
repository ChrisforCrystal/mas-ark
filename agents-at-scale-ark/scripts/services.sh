#!/usr/bin/env bash

# Services installation script to enable additional capabilities

set -e -o pipefail

# Colors for output
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[1;33m'
white='\033[1;37m'
blue='\033[0;34m'
purple='\033[0;35m'
nc='\033[0m'

# Parse command line arguments
MAKE_OPTS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            MAKE_OPTS="-n"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run]"
            exit 1
            ;;
    esac
done

services_setup() {
    # Check if we're in the project root
    if [ ! -f "version.txt" ]; then
        echo -e "${red}error${nc}: must run from project root directory"
        exit 1
    fi

    # Show version banner
    version=$(cat version.txt | tr -d '\n')
    echo -e "${green}agents-at-scale${nc} services setup ${white}v${version}${nc}"
    echo
    echo "for each service, choose: [s]kip, [d]ev mode, [i]nstall, [u]ninstall"
    if [ -n "$MAKE_OPTS" ]; then
        echo -e "${yellow}DRY RUN MODE${nc}: Commands will be shown but not executed"
    fi
    
    # Array to collect dev mode commands
    declare -a dev_commands=()

    # Find all services with build.mk files
    for service_dir in services/*/; do
        service_name=$(basename "$service_dir")
        build_file="${service_dir}build.mk"
        
        if [ ! -f "$build_file" ]; then
            continue
        fi
        
        # Skip services without manifest files
        manifest_file="${service_dir}manifest.yaml"
        if [ ! -f "$manifest_file" ]; then
            continue
        fi
        
        # Check if the build.mk contains install, uninstall, or dev targets
        # Look for patterns like "$(SERVICE_NAME)-install:" or "SERVICE-install:"
        # The service name in the variable might have underscores instead of hyphens
        service_var_pattern=$(echo "$service_name" | tr '-' '_' | tr '[:lower:]' '[:upper:]')
        
        supports_install=$(grep -E "(^${service_name}-install:|^\\$\\(${service_var_pattern}_SERVICE_NAME\\)-install:)" "$build_file" 2>/dev/null || true)
        supports_uninstall=$(grep -E "(^${service_name}-uninstall:|^\\$\\(${service_var_pattern}_SERVICE_NAME\\)-uninstall:)" "$build_file" 2>/dev/null || true)
        supports_dev=$(grep -E "(^${service_name}-dev:|^\\$\\(${service_var_pattern}_SERVICE_NAME\\)-dev:)" "$build_file" 2>/dev/null || true)
        if [ -f "$manifest_file" ] && yq eval '.' "$manifest_file" >/dev/null 2>&1; then
            name=$(yq eval '.name // "unknown"' "$manifest_file" 2>/dev/null || echo "$service_name")
            desc=$(yq eval '.description // "No description"' "$manifest_file" 2>/dev/null || echo "No description")
        else
            name="$service_name"
            desc="Service (no manifest.yaml)"
        fi
        
        echo -e "\n${blue}${name}${nc}: ${desc}"
        
        # Check if service is already deployed (for cluster services)
        if [ -n "$supports_install" ] && kubectl get deployment "$service_name" >/dev/null 2>&1; then
            echo -e "${green}✔${nc} ${name} deployed to cluster"
        fi
        
        if [ "${ARK_SERVICES_AUTO_INSTALL:-}" = "1" ]; then
            REPLY="i"
            echo "${name} action (s/d/i/u): i"
        else
            read -p "${name} action (s/d/i/u): " -r
        fi
        case $REPLY in
            [Dd])
                if [ -n "$supports_dev" ]; then
                    dev_commands+=("make ${service_name}-dev")
                    echo -e "${yellow}dev mode${nc}: will show command at end"
                else
                    echo -e "${yellow}note${nc}: ${name} does not support dev mode"
                fi
                ;;
            [Ii])
                if [ -n "$supports_install" ]; then
                    echo "installing ${name}..."
                    # Force the install target to run even if a local stamp file exists,
                    # to avoid stale local state when the Kubernetes cluster has changed
                    if make -B ${MAKE_OPTS} ${service_name}-install; then
                        echo -e "${green}✔${nc} ${name} installed successfully"
                        
                        # Check for and display post-install instructions
                        post_install=$(yq eval '.post-install-instructions // ""' "$manifest_file" 2>/dev/null)
                        if [ -n "$post_install" ]; then
                            echo -e "${yellow}Post-install instructions:${nc}"
                            echo -e "${yellow}${post_install}${nc}"
                        fi
                    else
                        echo -e "${red}error${nc}: failed to install ${name}"
                    fi
                else
                    echo -e "${yellow}note${nc}: ${name} does not support install"
                fi
                ;;
            [Uu])
                if [ -n "$supports_uninstall" ]; then
                    echo "uninstalling ${name}..."
                    if make ${MAKE_OPTS} ${service_name}-uninstall; then
                        echo -e "${green}✔${nc} ${name} uninstalled successfully"
                    else
                        echo -e "${red}error${nc}: failed to uninstall ${name}"
                    fi
                else
                    echo -e "${yellow}note${nc}: ${name} does not support uninstall"
                fi
                ;;
            *)
                echo "skipping ${name}"
                ;;
        esac
    done

    echo -e "\n${green}services setup complete!${nc}"
    
    # Show dev mode commands if any were selected
    if [ ${#dev_commands[@]} -gt 0 ]; then
        echo
        echo -e "${blue}To run services in dev mode:${nc}"
        for cmd in "${dev_commands[@]}"; do
            echo -e "  ${white}${cmd}${nc}"
        done
    fi
    
}

# Run the services setup
services_setup