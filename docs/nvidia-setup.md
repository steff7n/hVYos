# NVIDIA GPU Setup

Linta provides `linta-nvidia` for one-command NVIDIA driver setup on RPM Fusion. This guide covers setup, status checks, hybrid GPUs, and troubleshooting.

---

## Check for NVIDIA Hardware

```bash
$ lspci | grep -i nvidia
```

If you see one or more NVIDIA devices, proceed with setup.

---

## Quick Setup

```bash
$ sudo linta-nvidia setup
```

This runs the full configuration. Requires a reboot after completion.

---

## What Setup Does

1. **Enables RPM Fusion repositories** — free and nonfree
2. **Installs `akmod-nvidia`** — kernel modules built automatically (akmods/DKMS)
3. **Configures Wayland support:**
   - GBM backend (`GBM_BACKEND=nvidia-drm`)
   - nvidia-drm modeset and fbdev
   - Suspend/resume systemd integration
   - Initramfs rebuild
4. **Hybrid laptops:** Creates `prime-run` wrapper and udev power management rules
5. **Profile-specific tweaks** — KDE Xwayland behavior; Niri pure-Wayland configuration

---

## Status Check

```bash
$ linta-nvidia status
```

Shows GPU model, driver version, hybrid status, and Wayland readiness.

JSON output:

```bash
$ linta-nvidia status --json
```

---

## Hybrid GPU Laptops

On systems with integrated + discrete NVIDIA (e.g. Intel + NVIDIA), the discrete GPU is typically off by default. Use **PRIME offloading** to run specific apps on the NVIDIA GPU:

```bash
$ prime-run <application>
```

Example:

```bash
$ prime-run glxgears
```

For games or GPU-heavy apps, prefix the launch command with `prime-run`.

---

## Troubleshooting

### Black Screen After Boot

- Try the `nomodeset` kernel parameter from the GRUB menu.
- Boot into a snapshot from GRUB (if available) and run `sudo linta-nvidia uninstall`, then reboot. Re-attempt setup after verifying basic graphics work with nouveau.

### Wayland Session Does Not Start

- Ensure setup completed and you have rebooted.
- Check `linta-nvidia status` for Wayland readiness.
- On hybrid systems, try `prime-run` for the compositor if the default output is incorrect.

### Suspend/Resume Issues

- Setup configures suspend/resume integration; if problems persist, check journalctl for NVIDIA-related errors.

### Nouveau Conflicts

- `linta-nvidia setup` blacklists nouveau. If you previously had manual NVIDIA config, remove conflicting files (e.g. `/etc/modprobe.d/*nvidia*`) before running setup.

---

## Uninstalling

```bash
$ sudo linta-nvidia uninstall
```

Removes the NVIDIA driver, restores nouveau, and reverts Wayland configuration. Reboot after uninstall.
