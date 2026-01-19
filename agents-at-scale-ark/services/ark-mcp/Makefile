include ../../helpers.mk

# Local ark-mcp convenience commands
.DEFAULT_GOAL := help

# Service variables
ARK_MCP_DEFAULT_NAMESPACE ?= default
ARK_MCP_PORT ?= 2627

.PHONY: help dev install uninstall build

help: # show help for each of the Makefile recipes
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

build: # build Docker image
	@$(MAKE) -C ../.. ark-mcp-build

install: # deploy to cluster
	@$(MAKE) -C ../.. ark-mcp-install

uninstall: # remove from cluster
	@$(MAKE) -C ../.. ark-mcp-uninstall

clean-stamps: # clean dependencies
	@$(MAKE) -C ../.. ark-mcp-clean-stamps

dev: # run MCP server locally for development
	@echo "Starting ark-mcp server on port $(ARK_MCP_PORT)..."
	@cd ark-mcp && ARK_MCP_DEFAULT_NAMESPACE=$(ARK_MCP_DEFAULT_NAMESPACE) uv run python -m ark_mcp
