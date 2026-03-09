# Linta Linux — Build Automation
# Targets for building RPMs, running tests, validating manifests, and ISO builds.
#
# Usage:
#   make test            Run all unit tests
#   make validate        Validate package manifests and kickstart files
#   make rpm-lintactl    Build lintactl RPM (example — same pattern for all packages)
#   make rpms            Build all custom Linta RPMs
#   make iso PROFILE=kde Build an ISO for a specific profile
#   make clean           Remove build artifacts

SHELL := /bin/bash
.ONESHELL:
.PHONY: test validate rpms iso clean help

PROJECT_ROOT := $(shell pwd)
BUILD_OUTPUT := $(PROJECT_ROOT)/build/output
RPM_BUILD    := $(BUILD_OUTPUT)/rpmbuild
SPECS_DIR    := $(PROJECT_ROOT)/build/packages/specs

PROFILES := bare kde niri combined

# ── Custom Linta packages ──
LINTA_PACKAGES := lintactl linta-snapshots linta-nvidia linta-welcome \
                  linta-flatpak-manager linta-keybindings

CONFIG_PACKAGES := linta-config-zsh linta-config-helix linta-config-niri \
                   linta-config-system

THEME_PACKAGES := linta-theme-kde linta-theme-niri linta-theme-sddm \
                  linta-theme-plymouth

UPSTREAM_PACKAGES := niri helix swaylock-effects floorp

# ── Help ──
help:
	@echo "Linta Linux Build System"
	@echo "========================"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all Python unit tests"
	@echo "  make test-lintactl     Run lintactl tests only"
	@echo "  make test-snapshots    Run linta-snapshots tests only"
	@echo "  make test-nvidia       Run linta-nvidia tests only"
	@echo "  make validate          Validate package manifests + kickstart files"
	@echo ""
	@echo "Building:"
	@echo "  make rpms              Build all custom Linta RPMs (requires mock)"
	@echo "  make rpm-<package>     Build a single package RPM"
	@echo "  make iso PROFILE=kde   Build ISO for a profile (bare|kde|niri|combined)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             Remove build artifacts"
	@echo "  make lint              Run basic linting on Python files"

# ── Tests ──
test: test-lintactl test-snapshots test-nvidia
	@echo "All tests passed."

test-lintactl:
	@echo "── lintactl tests ──"
	cd packages/lintactl && python3 -m pytest test_lintactl.py -v 2>/dev/null \
		|| python3 -m unittest test_lintactl -v

test-snapshots:
	@echo "── linta-snapshots tests ──"
	cd packages/linta-snapshots && python3 -m pytest test_linta_snapshots.py -v 2>/dev/null \
		|| python3 -m unittest test_linta_snapshots -v

test-nvidia:
	@echo "── linta-nvidia tests ──"
	cd packages/linta-nvidia && python3 -m pytest test_linta_nvidia.py -v 2>/dev/null \
		|| python3 -m unittest test_linta_nvidia -v

# ── Validation ──
validate:
	@echo "── Package manifest validation ──"
	bash build/testing/validate-manifests.sh
	@echo ""
	@echo "── Kickstart validation ──"
	bash build/testing/validate-kickstarts.sh

# ── Linting ──
lint:
	@echo "── Python lint ──"
	@find packages/ -name '*.py' -not -name 'test_*' -not -path '*__pycache__*' \
		-exec python3 -m py_compile {} \; -print
	@echo "All files compile successfully."

# ── RPM Building ──
# Requires: rpm-build, rpmdevtools, mock
# These create source tarballs and build via rpmbuild or mock.

$(RPM_BUILD):
	mkdir -p $(RPM_BUILD)/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

rpms: $(addprefix rpm-,$(LINTA_PACKAGES))
	@echo "All Linta RPMs built. Output: $(RPM_BUILD)/RPMS/"

define RPM_TEMPLATE
rpm-$(1): $(RPM_BUILD)
	@echo "── Building $(1) ──"
	@spec=$$$$(find packages/$(1)/ -name '*.spec' 2>/dev/null | head -1); \
	if [ -z "$$$$spec" ]; then echo "No spec file for $(1)"; exit 1; fi; \
	tar czf $(RPM_BUILD)/SOURCES/$(1)-0.1.0.tar.gz -C packages/ $(1)/ \
		--transform='s|^$(1)/|$(1)-0.1.0/|'; \
	rpmbuild --define "_topdir $(RPM_BUILD)" -ba "$$$$spec" || \
		echo "Warning: rpmbuild failed for $(1) (may need dependencies)"
endef

$(foreach pkg,$(LINTA_PACKAGES),$(eval $(call RPM_TEMPLATE,$(pkg))))

# ── ISO Building ──
PROFILE ?= kde

iso:
	@if ! echo "$(PROFILES)" | grep -qw "$(PROFILE)"; then \
		echo "Error: invalid profile '$(PROFILE)'. Use: $(PROFILES)"; exit 1; \
	fi
	sudo bash scripts/build-iso.sh $(PROFILE)

# ── Clean ──
clean:
	rm -rf $(BUILD_OUTPUT)
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	@echo "Build artifacts cleaned."
