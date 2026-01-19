# Local Makefile for tools/ark-cli
MAKEFILE_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PROJECT_ROOT := $(abspath $(MAKEFILE_DIR)/../../)

.PHONY: build install dev test uninstall clean help

# Delegate to root makefile with ark-cli prefix
build: ## Build ark-cli
	cd $(PROJECT_ROOT) && make ark-cli-build

install: ## Install ark-cli globally
	cd $(PROJECT_ROOT) && make ark-cli-install

dev: ## Run ark-cli in development mode
	cd $(PROJECT_ROOT) && make ark-cli-dev

test: ## Run ark-cli tests
	cd $(PROJECT_ROOT) && make ark-cli-test

uninstall: ## Uninstall ark-cli
	cd $(PROJECT_ROOT) && make ark-cli-uninstall

clean: ## Clean local build artifacts
	rm -rf dist node_modules coverage
	rm -f $(PROJECT_ROOT)/out/ark-cli/stamp-*

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)