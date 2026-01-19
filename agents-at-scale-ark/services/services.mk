# Services makefile fragment - dynamically discover services with build.mk files

# Find all services that have a build.mk file
SERVICE_BUILD_MKS := $(wildcard services/*/build.mk)
SERVICES := $(patsubst services/%/build.mk,%,$(SERVICE_BUILD_MKS))

# Include all service build.mk files
-include $(SERVICE_BUILD_MKS)

# Aggregate targets for all services
.PHONY: services-build-all services-install-all services-uninstall-all services-test-all

services-build-all: $(foreach svc,$(SERVICES),$(svc)-build) # HELP: Build all services
services-install-all: $(foreach svc,$(SERVICES),$(svc)-install) # HELP: Install all services to cluster
services-uninstall-all: $(foreach svc,$(SERVICES),$(svc)-uninstall) # HELP: Uninstall all services from cluster
services-test-all: $(foreach svc,$(SERVICES),$(svc)-test) # HELP: Run tests for all services
