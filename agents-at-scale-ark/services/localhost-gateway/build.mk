# localhost-gateway service build configuration

LOCALHOST_GATEWAY_SERVICE_NAME := localhost-gateway
LOCALHOST_GATEWAY_SERVICE_DIR := services/$(LOCALHOST_GATEWAY_SERVICE_NAME)
LOCALHOST_GATEWAY_OUT := $(OUT)/$(LOCALHOST_GATEWAY_SERVICE_NAME)

# Service-specific variables
LOCALHOST_GATEWAY_NAMESPACE ?= ark-system
LOCALHOST_GATEWAY_PORT ?= 8080

# Pre-calculate all stamp paths
LOCALHOST_GATEWAY_STAMP_BUILD := $(LOCALHOST_GATEWAY_OUT)/stamp-build
LOCALHOST_GATEWAY_STAMP_INSTALL := $(LOCALHOST_GATEWAY_OUT)/stamp-install
LOCALHOST_GATEWAY_STAMP_TEST := $(LOCALHOST_GATEWAY_OUT)/stamp-test

# Add service output directory to clean targets
CLEAN_TARGETS += $(LOCALHOST_GATEWAY_OUT)

# Define phony targets
.PHONY: $(LOCALHOST_GATEWAY_SERVICE_NAME)-build $(LOCALHOST_GATEWAY_SERVICE_NAME)-install $(LOCALHOST_GATEWAY_SERVICE_NAME)-uninstall $(LOCALHOST_GATEWAY_SERVICE_NAME)-test

# Build target (no build needed for Helm chart)
$(LOCALHOST_GATEWAY_SERVICE_NAME)-build: $(LOCALHOST_GATEWAY_STAMP_BUILD) # HELP: Build localhost-gateway (pre-built images)
$(LOCALHOST_GATEWAY_STAMP_BUILD): | $(OUT)
	@mkdir -p $(dir $@)
	@echo "localhost-gateway uses pre-built images - no build needed"
	@touch $@

# Install target
$(LOCALHOST_GATEWAY_SERVICE_NAME)-install: $(LOCALHOST_GATEWAY_STAMP_INSTALL) # HELP: Deploy localhost-gateway with Gateway API CRDs
$(LOCALHOST_GATEWAY_STAMP_INSTALL): $(LOCALHOST_GATEWAY_SERVICE_DIR)/install-gateway.sh | $(OUT)
	@mkdir -p $(dir $@)
	LOCALHOST_GATEWAY_SERVICE_NAME="$(LOCALHOST_GATEWAY_SERVICE_NAME)" \
	LOCALHOST_GATEWAY_SERVICE_DIR="$(LOCALHOST_GATEWAY_SERVICE_DIR)" \
	LOCALHOST_GATEWAY_NAMESPACE="$(LOCALHOST_GATEWAY_NAMESPACE)" \
	LOCALHOST_GATEWAY_PORT="$(LOCALHOST_GATEWAY_PORT)" \
	$(LOCALHOST_GATEWAY_SERVICE_DIR)/install-gateway.sh
	@touch $@

# Uninstall target
$(LOCALHOST_GATEWAY_SERVICE_NAME)-uninstall: # HELP: Remove localhost-gateway from cluster
	@echo "Stopping port-forwarding..."
	pkill -f "kubectl.*port-forward.*$(LOCALHOST_GATEWAY_PORT):80" || true
	@echo "Uninstalling localhost-gateway..."
	helm uninstall $(LOCALHOST_GATEWAY_SERVICE_NAME) --namespace $(LOCALHOST_GATEWAY_NAMESPACE) --ignore-not-found
	@echo "localhost-gateway uninstalled successfully"
	rm -f $(LOCALHOST_GATEWAY_STAMP_INSTALL)

# Test target
$(LOCALHOST_GATEWAY_SERVICE_NAME)-test: $(LOCALHOST_GATEWAY_STAMP_TEST) # HELP: Run tests for localhost-gateway service
$(LOCALHOST_GATEWAY_STAMP_TEST): $(LOCALHOST_GATEWAY_STAMP_BUILD) | $(OUT)
	@mkdir -p $(dir $@)
	@printf '\033[0;31m⚠️  NO TESTS ARE DEFINED for $(LOCALHOST_GATEWAY_SERVICE_NAME)\033[0m\n'
	@touch $@