# Bug Report V2

## Findings

### Build and test

1. `scripts/run-tests.sh` exits immediately because `set -e` treats `((TOTAL++))` as a failure when `TOTAL` starts at `0`.
2. `build/container-entry.sh test` has the same arithmetic bug and only runs a subset of the repo test suites.
3. `build/mock/linta-fc42-x86_64.cfg` uses `baseurl=` with mirrorlist endpoints, which breaks repo resolution.
4. `build/container-entry.sh` uses `livecd-creator` while `scripts/build-iso.sh` uses `livemedia-creator`, so the two ISO paths diverge.
5. `build/testing/validate-manifests.sh` silently turns `dnf repoquery` failures into a wall of false package misses.
6. `build/testing/validate-kickstarts.sh` flattens kickstarts without an explicit Fedora version.

### Installer

1. Pressing `Back` on the confirmation screen still proceeds into installation.
2. The selected install profile is not used to choose packages.
3. The TUI installer does not create `/etc/linta-release`.
4. The TUI installer does not create the default user expected by the distro flow.
5. The installer hardcodes `--releasever 41`.

### Runtime and packaging

1. `lintactl` defaults Niri to `linta-niri-rice1`, but the installed theme directories are `linta-niri-rice-1` through `-4`.
2. `linta-welcome` offers `Breeze` and `Vanilla Niri`, but applying them is a no-op.
3. `linta-welcome` collects locale/timezone choices but never applies them.
4. The SDDM theme references `background.png`, but the asset is missing from the package.
5. Waybar memory formatting uses `{}` instead of `{percentage}` in some generated/shipped configs.
6. The Niri configs reference a wallpaper path that is not provided in the repo and use `foot` without ensuring it is installed.
7. `build/packages/linta-custom.txt` names non-existent `linta-theme-niri-rice*` RPMs instead of the real `linta-theme-niri` package.
8. `linta-snapshots` generates GRUB entries with invalid kernel/initramfs paths for snapshots.
9. `linta-snapshots.spec` lists `__pycache__` artifacts that are not installed.

## Planned Fix Order

1. Repair the build/test entrypoints so the repo can validate itself reliably.
2. Align the mock and ISO build configuration.
3. Fix installer control-flow and metadata correctness.
4. Fix runtime/package/theme consistency issues.

## Fix Log

### 2026-03-09 - Build/test entrypoints

- Fixed `scripts/run-tests.sh` so arithmetic counters do not trip `set -e`.
- Fixed `build/container-entry.sh test` to avoid the same early-exit bug and to run the same eight suite slots covered by `make test`.
- Aligned `build/container-entry.sh build-iso` with the standalone `livemedia-creator` flow instead of the older `livecd-creator` path.
- Fixed `build/mock/linta-fc42-x86_64.cfg` to use `mirrorlist=` for Fedora mirrorlist endpoints.
- Fixed `build/testing/validate-manifests.sh` to fail explicitly when `dnf repoquery` is unavailable instead of silently reporting every package as missing.
- Fixed `build/testing/validate-kickstarts.sh` to pass an explicit Fedora version to `ksflatten`.
- Expanded `make test` and the container `test` entrypoint so the new `build/testing` regression files are part of the scripted test path instead of being skipped.
- Updated `build/README.md` and `scripts/build-iso.sh` text to match the current ISO tooling.

Targeted verification:

- `python3 -m pytest build/testing/test_build_entrypoints.py -v` -> passed (`7 passed`)
- `bash scripts/run-tests.sh` now runs both slots and reports the real downstream validation failures instead of exiting at the header

### 2026-03-09 - Installer and system configuration

- Fixed the confirmation-screen `Back` path so the installer returns to the selection flow instead of falling through into installation.
- Added profile-aware package selection so `bare`, `kde`, `niri`, and `combined` installs now produce different payloads.
- Added helper-driven system configuration that always writes `hostname`, `locale.conf`, `/etc/localtime`, and `/etc/linta-release`.
- Added creation of the default installer user (`linta`) so the TUI path matches the distro's existing login workflow.
- Updated the installer DNF command to use the current repo default releasever (`42`) instead of the stale hardcoded `41`.

Targeted verification:

- `cd installer && python3 -m pytest test_linta_installer.py -v` -> passed (`6 passed`)

### 2026-03-09 - Runtime and packaging consistency

- Fixed `lintactl` so the default Niri theme ID matches the shipped theme directory name (`linta-niri-rice-1`).
- Removed unsupported `Breeze` and `Vanilla Niri` choices from `linta-welcome`, added a shared theme resolver, and applied locale/timezone selections through privileged system tools.
- Fixed snapshot GRUB generation to use versioned kernel/initramfs names under each snapshot's `boot/` directory.
- Corrected Waybar memory placeholders in the theme designer and shipped Niri rice configs.
- Removed references to the missing SDDM background asset and kept the theme on its solid-color fallback.
- Removed the missing Niri wallpaper reference from shipped configs/kickstarts and added `foot` where the configs expect it.
- Corrected `build/packages/linta-custom.txt` to reference the real `linta-theme-niri` package.
- Removed the nonexistent `__pycache__` entry from `packages/linta-snapshots/linta-snapshots.spec`.

Targeted verification:

- `cd packages/lintactl && python3 -m pytest test_lintactl.py -k niri_profile_default -v` -> passed
- `cd packages/linta-welcome && python3 -m pytest test_linta_welcome.py -k 'ThemePickerOptions or ThemeMap or LocaleApplication' -v` -> passed
- `cd packages/linta-snapshots && python3 -m pytest test_linta_snapshots.py -k 'boot_artifacts or concrete_uuid' -v` -> passed
- `python3 -m pytest build/testing/test_runtime_configs.py -v` -> passed (`6 passed`)

## Verification

Initial pre-fix evidence:

- `pytest -q` passed during investigation.
- `make test` passed during investigation.
- `bash scripts/run-tests.sh` failed immediately after printing its header.
- `bash -x scripts/run-tests.sh` showed the early exit at `(( TOTAL++ ))`.

Final post-fix evidence:

- `pytest -q` -> passed (`101 passed`)
- `make test` -> passed
- `bash scripts/run-tests.sh` -> runner itself works; on this Manjaro host it now fails explicitly because `dnf` and `ksvalidator` are not installed, instead of failing misleadingly or exiting at the header
