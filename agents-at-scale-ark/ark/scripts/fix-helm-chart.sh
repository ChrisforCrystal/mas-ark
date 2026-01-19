#!/usr/bin/env bash
set -euo pipefail

# Fix kubebuilder helm plugin naming issues
# Replaces controller-manager with ark-controller throughout the chart

echo "Fixing Helm chart naming..."

# Fix manager deployment
if [ -f "dist/chart/templates/manager/manager.yaml" ]; then
    sed -i.bak 's/name: ark-controller-manager/name: ark-controller/g' dist/chart/templates/manager/manager.yaml
    sed -i.bak 's/control-plane: controller-manager/control-plane: ark-controller/g' dist/chart/templates/manager/manager.yaml
    rm -f dist/chart/templates/manager/manager.yaml.bak
fi

# Fix webhook service
if [ -f "dist/chart/templates/webhook/service.yaml" ]; then
    sed -i.bak 's/control-plane: controller-manager/control-plane: ark-controller/g' dist/chart/templates/webhook/service.yaml
    rm -f dist/chart/templates/webhook/service.yaml.bak
fi

# Fix metrics service (if it exists)
if [ -f "dist/chart/templates/metrics/metrics_service.yaml" ]; then
    sed -i.bak 's/control-plane: controller-manager/control-plane: ark-controller/g' dist/chart/templates/metrics/metrics_service.yaml
    rm -f dist/chart/templates/metrics/metrics_service.yaml.bak
fi

# Add missing values to values.yaml
if ! grep -q "containerRegistry:" dist/chart/values.yaml; then
    cat >> dist/chart/values.yaml << 'EOF'

# Container registry configuration
containerRegistry:
  enabled: false
  server: ""
  username: ""
  password: ""
  email: ""
EOF
fi

echo "✅ Fixed Helm chart naming"