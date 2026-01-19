STAMP_BUNDLES=$(OUT)/bundles-stamp

BUNDLE_DIRS := $(shell find bundles -type f -name manifest.yaml)
BUNDLE_NAMES := $(word 2,$(subst /, ,$(BUNDLE_DIRS)))
BUNDLE_ZIPS := $(addprefix $(OUT)/bundle-,$(addsuffix .zip,$(BUNDLE_NAMES)))

$(OUT)/bundle-%.zip: $(shell find bundles/$* -type f) | $(OUT)
	cd bundles/$* && zip -qr "$(abspath $@)" components 

$(STAMP_BUNDLES): $(BUNDLE_ZIPS) | $(OUT)
	touch $@

.PHONY: bundles
bundles: $(STAMP_BUNDLES)
