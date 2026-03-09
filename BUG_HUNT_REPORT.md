# Bug Hunt Report

Generated on 2026-03-09.

This report now reflects the implemented fixes, not just the initial findings. All eight reported bugs were reproduced, fixed, and verified with targeted tests and runtime evidence.

## Summary

- Fixed bugs: 8
- Targeted regression tests: 48 passing
- Production compile check: passing
- Debug instrumentation: removed after successful verification

## Fixed bugs

### 1. `lintactl theme set` path traversal

- Status: fixed
- File: `packages/lintactl/lintactl.py`
- Root cause: theme names were accepted as raw paths, so `../evil` could escape `THEMES_DIR`.
- Implemented fix:
  - added `_is_valid_theme_name()` to reject traversal/path-separator inputs
  - kept a containment check using resolved paths as defense in depth
  - stopped invalid names before `apply.sh` can run
- Verification:
  - regression test `test_cmd_theme_set_rejects_path_traversal` passes
  - post-fix log shows `theme_name: "../evil"` with `is_valid_theme_name: false` and `is_within_theme_dir: false`

### 2. `linta-snapshots` generated GRUB entries with `$btrfs_uuid`

- Status: fixed
- File: `packages/linta-snapshots/linta_snapshots.py`
- Root cause: generated GRUB entries referenced a shell variable that the script never defined.
- Implemented fix:
  - added `_get_root_uuid()` using `findmnt`
  - embedded the concrete UUID directly into generated `search` and `root=UUID=` lines
  - fail the command with a clear error if the UUID cannot be determined
- Verification:
  - regression test `test_update_grub_entries_embeds_concrete_uuid` passes
  - post-fix log records `uses_literal_uuid_variable: false` and `root_uuid: "1234-ABCD"`

### 3. `lintactl info` mislabeled non-Btrfs roots

- Status: fixed
- File: `packages/lintactl/lintactl.py`
- Root cause: one variable was used both for filesystem type and for Btrfs status wording.
- Implemented fix:
  - split filesystem type from Btrfs status
  - print `Filesystem: <actual fs>` for non-Btrfs roots
  - keep `Btrfs (active)` only when the root filesystem is actually `btrfs`
  - added a `filesystem` field to JSON output while preserving `btrfs` status
- Verification:
  - regression test `test_cmd_info_non_btrfs_prints_actual_filesystem` passes
  - post-fix log shows `filesystem_value: "ext4"` with `btrfs_status: "inactive"`

### 4. `linta-nvidia setup` always made a broken first RPM Fusion request

- Status: fixed
- File: `packages/linta-nvidia/linta_nvidia.py`
- Root cause: the code built a literal URL containing `$(rpm -E %fedora)` even though the subprocess call does not invoke a shell.
- Implemented fix:
  - added `_rpm_fusion_releasever()`
  - resolve Fedora version before building URLs
  - removed the guaranteed-failing first install attempt and fallback dance
- Verification:
  - regression test `test_enable_rpm_fusion_uses_expanded_release_urls` passes
  - post-fix log shows fully expanded URLs ending in `42.noarch.rpm`

### 5. Installer built wrong NVMe partition paths

- Status: fixed
- File: `installer/linta_installer.py`
- Root cause: partition paths were built with direct string concatenation, which breaks on device names that already end in a digit.
- Implemented fix:
  - added `_partition_device(disk, number)`
  - switched format/mount calls to use the helper
  - preserved existing behavior for `/dev/sdX` disks
- Verification:
  - regression test `test_partition_device_handles_nvme_and_sata_names` passes
  - post-fix runtime harness shows `/dev/nvme0n1p1`, `/dev/nvme0n1p2`, and `/dev/nvme0n1p3`
  - post-fix log records the corrected partition device derivation

### 6. `linta-welcome` first-boot marker write failed for normal users

- Status: fixed
- Files:
  - `packages/linta-welcome/linta_welcome.py`
  - `packages/linta-welcome/linta-welcome-firstboot.service`
  - `packages/linta-welcome/linta-welcome.desktop`
  - `packages/linta-welcome/README.md`
- Root cause: a user-scoped wizard tried to write a system-scoped marker under `/var/lib/linta`.
- Implemented fix:
  - moved the default marker to `${XDG_STATE_HOME:-$HOME/.local/state}/linta/first-boot-done`
  - updated the user service and autostart entry to check the same per-user marker
  - made marker write failure non-fatal
- Verification:
  - regression test `test_accept_does_not_crash_when_marker_write_is_denied` passes
  - post-fix success harness writes the marker under a temporary `XDG_STATE_HOME`
  - post-fix log records `first boot marker written`

### 7. `scripts/build-with-container.sh` used a Podman-only image check for Docker

- Status: fixed
- File: `scripts/build-with-container.sh`
- Root cause: the script always used `image exists`, which Docker does not support.
- Implemented fix:
  - added `image_missing()` to branch by runtime
  - use `docker image inspect` for Docker
  - keep `podman image exists` behavior for Podman-like runtimes
- Verification:
  - regression test `test_docker_runtime_uses_docker_supported_image_check` passes
  - post-fix log records `strategy: "docker-image-inspect"`

### 8. `linta-keybindings` crashed when no primary screen existed

- Status: fixed
- File: `packages/linta-keybindings/linta_keybindings.py`
- Root cause: `showEvent()` dereferenced `QApplication.primaryScreen()` without a `None` guard.
- Implemented fix:
  - guard the missing-screen case
  - keep the default overlay size and place the window at `(0, 0)` instead of crashing
- Verification:
  - regression test `test_show_event_handles_missing_primary_screen` passes
  - post-fix log still shows `has_primary_screen: false`, but the test now completes successfully

## Verification commands

The final verification pass used:

- `python3 -m pytest packages/lintactl/test_lintactl.py packages/linta-snapshots/test_linta_snapshots.py packages/linta-nvidia/test_linta_nvidia.py packages/linta-welcome/test_linta_welcome.py packages/linta-keybindings/test_linta_keybindings.py installer/test_linta_installer.py build/testing/test_build_with_container.py -v`
- `make lint`
- targeted post-fix runtime harnesses for:
  - welcome marker creation under a temporary `XDG_STATE_HOME`
  - installer NVMe partition derivation during `run_install()`
