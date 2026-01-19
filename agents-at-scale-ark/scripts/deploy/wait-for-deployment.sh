#!/usr/bin/env bash

# Wait for Helm release to be ready

set -e

RELEASE=${1:-ark-controller}
NAMESPACE=${2:-ark-system}
TIMEOUT=${3:-300}

echo "Waiting for Helm release $RELEASE in namespace $NAMESPACE..."

ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    echo "--- Status at ${ELAPSED}s ---"
    
    # Show Helm release status
    helm status $RELEASE -n $NAMESPACE 2>/dev/null || echo "Release not found yet"
    
    # Show pods for this release
    kubectl get pods -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE --no-headers 2>/dev/null || echo "No pods for release yet"
    
    # Check if release is deployed and ready
    if helm status $RELEASE -n $NAMESPACE -o json 2>/dev/null | jq -r '.info.status' | grep -q "deployed"; then
        # Double-check that pods are actually ready
        if kubectl get pods -n $NAMESPACE -l app.kubernetes.io/instance=$RELEASE -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null | grep -q "True"; then
            echo "✅ Helm release is deployed and ready!"
            exit 0
        fi
    fi
    
    sleep 10
    ELAPSED=$((ELAPSED + 10))
done

echo "❌ Release timed out after ${TIMEOUT}s"
helm status $RELEASE -n $NAMESPACE 2>/dev/null || echo "Release not found"
exit 1