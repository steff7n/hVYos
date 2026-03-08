# linta-nvidia

NVIDIA GPU setup tool for Linta Linux.

## Commands

| Command | Description |
|---|---|
| `sudo linta-nvidia setup` | Full setup: RPM Fusion, akmod driver, Wayland config, hybrid GPU, profile quirks |
| `linta-nvidia status` | Show GPU model, driver version, hybrid status, Wayland readiness |
| `linta-nvidia status --json` | Same, JSON output |
| `sudo linta-nvidia uninstall` | Remove NVIDIA driver and restore nouveau |

## What `setup` does

1. Enables RPM Fusion free + nonfree repositories
2. Installs `akmod-nvidia` (auto-builds kernel modules via DKMS/akmods)
3. Configures Wayland compatibility:
   - GBM backend (`GBM_BACKEND=nvidia-drm`)
   - nvidia-drm modeset + fbdev
   - Suspend/resume systemd services
   - Initramfs rebuild
4. For hybrid laptops: creates `prime-run` wrapper + power management udev rules
5. Profile-specific quirks (KDE Xwayland, Niri pure Wayland)

## Profiles

Relevant to: **[KDE]**, **[Niri]**, **[Combined]**
Also works on **[Bare]** for compute use.

## Spec Reference

README.md §9.2
