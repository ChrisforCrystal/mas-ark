# fark service build configuration

FARK_SERVICE_NAME := fark
FARK_SERVICE_DIR := tools/$(FARK_SERVICE_NAME)
FARK_OUT := $(OUT)/$(FARK_SERVICE_NAME)

# Service-specific variables
FARK_BINARY := $(FARK_OUT)/fark
FARK_IMAGE := fark
FARK_TAG ?= latest

# Pre-calculate all stamp paths
FARK_STAMP_TEST := $(FARK_OUT)/stamp-test
FARK_STAMP_BUILD := $(FARK_OUT)/stamp-build
FARK_STAMP_INSTALL := $(FARK_OUT)/stamp-install

# Add service output directory to clean targets
CLEAN_TARGETS += $(FARK_OUT)
# Clean up Go artifacts
CLEAN_TARGETS += $(FARK_SERVICE_DIR)/cover.out
CLEAN_TARGETS += $(FARK_SERVICE_DIR)/.cover
CLEAN_TARGETS += $(FARK_SERVICE_DIR)/vendor

# Define phony targets
.PHONY: $(FARK_SERVICE_NAME)-build $(FARK_SERVICE_NAME)-install $(FARK_SERVICE_NAME)-dev $(FARK_SERVICE_NAME)-test $(FARK_SERVICE_NAME)-uninstall

# Test target
$(FARK_SERVICE_NAME)-test: $(FARK_STAMP_TEST)
$(FARK_STAMP_TEST): $(FARK_SERVICE_DIR)/go.mod $(FARK_SERVICE_DIR)/go.sum | $(OUT)
	@mkdir -p $(dir $@)
	cd $(FARK_SERVICE_DIR) && go fmt ./... && go vet ./... && go test ./... -coverprofile cover.out
	@touch $@

# Build binary
$(FARK_BINARY): $(FARK_STAMP_TEST) | $(OUT)
	@mkdir -p $(dir $@)
	cd $(FARK_SERVICE_DIR) && go mod vendor && go build -o $@ ./cmd/fark

# Build target (Docker)
$(FARK_SERVICE_NAME)-build: $(FARK_STAMP_BUILD)
$(FARK_STAMP_BUILD): $(FARK_BINARY)
	cd $(FARK_SERVICE_DIR) && docker build -t $(FARK_IMAGE):$(FARK_TAG) .
	@touch $@

# Install target
$(FARK_SERVICE_NAME)-install: $(FARK_STAMP_INSTALL)
$(FARK_STAMP_INSTALL): $(FARK_BINARY)
	@mkdir -p "$(HOME)/.local/bin" 2>/dev/null || true
	@echo "Installing fark to $(HOME)/.local/bin..."
	@if cp $(FARK_BINARY) "$(HOME)/.local/bin/fark" 2>/dev/null && chmod +x "$(HOME)/.local/bin/fark" 2>/dev/null; then \
		echo "fark installed to $(HOME)/.local/bin/fark"; \
		if ! echo "$$PATH" | grep -q "$(HOME)/.local/bin"; then \
			echo ""; \
			echo "NOTE: Please add $(HOME)/.local/bin to your PATH if not already added:"; \
			echo '  export PATH="$$HOME/.local/bin:$$PATH"'; \
		fi \
	else \
		echo "Failed to install fark to $(HOME)/.local/bin"; \
		echo "Attempting with /usr/local/bin..."; \
		if cp $(FARK_BINARY) /usr/local/bin/fark 2>/dev/null && chmod +x /usr/local/bin/fark 2>/dev/null; then \
			echo "fark installed to /usr/local/bin/fark"; \
		else \
			echo "Attempting with sudo..."; \
			sudo cp $(FARK_BINARY) /usr/local/bin/fark && \
			sudo chmod +x /usr/local/bin/fark && \
			echo "fark installed to /usr/local/bin/fark (with sudo)"; \
		fi \
	fi
	@touch $@

# Dev target
$(FARK_SERVICE_NAME)-dev: $(FARK_BINARY)
	$(FARK_BINARY)

# Uninstall target
$(FARK_SERVICE_NAME)-uninstall:
	@echo "Checking for fark installations..."
	@if [ -f "$(HOME)/.local/bin/fark" ]; then \
		echo "Removing fark from $(HOME)/.local/bin..."; \
		rm -f "$(HOME)/.local/bin/fark" && \
		echo "fark removed from $(HOME)/.local/bin"; \
	fi
	@if [ -f "/usr/local/bin/fark" ]; then \
		echo "Removing fark from /usr/local/bin..."; \
		if rm -f /usr/local/bin/fark 2>/dev/null; then \
			echo "fark removed from /usr/local/bin"; \
		else \
			echo "Attempting with sudo..."; \
			sudo rm -f /usr/local/bin/fark && \
			echo "fark removed from /usr/local/bin (with sudo)"; \
		fi; \
	fi
