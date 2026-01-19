# Tools makefile fragment - dynamically discover tools with build.mk files

# Find all tools that have a build.mk file
TOOL_BUILD_MKS := $(wildcard tools/*/build.mk)
TOOLS := $(patsubst tools/%/build.mk,%,$(TOOL_BUILD_MKS))

# Include all tool build.mk files
-include $(TOOL_BUILD_MKS)

# Aggregate targets for all tools
.PHONY: tools-build-all tools-install-all tools-uninstall-all tools-test-all

tools-build-all: $(foreach tool,$(TOOLS),$(tool)-build) # HELP: Build all tools
tools-install-all: $(foreach tool,$(TOOLS),$(tool)-install) # HELP: Install all tools
tools-uninstall-all: $(foreach tool,$(TOOLS),$(tool)-uninstall) # HELP: Uninstall all tools
tools-test-all: $(foreach tool,$(TOOLS),$(tool)-test) # HELP: Run tests for all tools