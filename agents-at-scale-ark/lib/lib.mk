# Library makefile fragment - dynamically discover libraries with build.mk files

# Find all libraries that have a build.mk file
LIB_BUILD_MKS := $(wildcard lib/*/build.mk)
LIBS := $(patsubst lib/%/build.mk,%,$(LIB_BUILD_MKS))

# Include all library build.mk files
-include $(LIB_BUILD_MKS)

# Aggregate targets for all libraries
.PHONY: libs-build-all libs-test-all

libs-build-all: $(foreach lib,$(LIBS),$(lib)-build) # HELP: Build all libraries
libs-test-all: $(foreach lib,$(filter-out ,$(LIBS)),$(lib)-test) # HELP: Run tests for all libraries