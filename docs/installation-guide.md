# Linta Installation Guide

This guide covers installing Linta Linux from a bootable USB.

---

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Architecture | 64-bit x86_64 | — |
| RAM | 2 GB | 4 GB or more |
| Disk space | 20 GB | 50 GB or more |
| Boot mode | **UEFI required** | — |

Linta does not support legacy BIOS. Secure Boot is optional — it will work with or without it.

---

## Downloading the ISO

Linta ships four profile-specific ISOs. Choose one based on your desired desktop:

| Profile | Size | Contents |
|---------|------|----------|
| **Bare** | ~1–1.2 GB | Base system, dev toolchain, shell, Helix, firmware, codecs — TTY only |
| **Niri** | ~1.5–2 GB | Bare + Niri compositor, Waybar, rices, Floorp, Flameshot, nomacs, fuzzel |
| **KDE** | ~2–2.5 GB | Bare + KDE Plasma, SDDM, Floorp, Flameshot, nomacs, KDE apps |
| **Combined** | ~2.5–3 GB | Bare + KDE + Niri — both environments, switchable at login |

Download from the official site and verify the SHA256 checksum before use.

---

## Creating a Bootable USB

### Using `dd` (Linux/macOS)

Replace `/dev/sdX` with your USB device (e.g. `/dev/sdb`). **This destroys all data on the target device.**

```bash
$ dd if=linta-niri.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

### Using Fedora Media Writer

1. Download [Fedora Media Writer](https://fedoraproject.org/workstation/download/)
2. Select “Write custom image” and choose your Linta ISO
3. Write to the target USB drive

---

## Booting the Installer

1. Plug in the USB drive
2. Reboot and enter your firmware boot menu (often F12, F2, Esc, or Del)
3. Select the USB drive from the UEFI boot entries
4. At the boot menu, choose **“Install Linta”** (default entry)

---

## TUI Installer Walkthrough

The installer is ncurses-based. Navigate with arrow keys and Enter.

### 1. Welcome

Introductory screen. Press Enter to continue.

### 2. Profile Selection

Choose one of four profiles:

- **KDE** — Full Plasma desktop with Linta theme. Wayland + Xwayland for compatibility.
- **Niri** — Scrollable tiling Wayland compositor. No Xwayland. Curated rice presets.
- **Combined** — Both KDE and Niri installed. Choose session at SDDM login.
- **Bare** — TTY only. Dev toolchain, shell, Helix. No display manager.

### 3. Hostname

An auto-generated hostname is suggested (e.g. `silent-pine`, `brave-otter`). Accept it or edit it before continuing.

### 4. Locale

Select your primary locale. English is always included; your language is added alongside it.

### 5. Timezone

Pick your timezone from the list. No automatic geolocation.

### 6. Disk Encryption

Optional LUKS2 full-disk encryption. **Off by default.** If enabled, you set a passphrase that unlocks the drive at boot.

### 7. Disk Selection

Choose the target drive for installation. All data on the selected disk will be removed.

### 8. Confirmation

Review hostname, profile, locale, timezone, encryption status, and target disk. Confirm to proceed. **This step performs destructive writes.**

### 9. Installation

The installer copies packages and configures the system. Wait until completion.

### 10. Complete

Installation is finished. Remove the USB drive and press Enter to reboot.

---

## Post-Install

On first boot (for KDE, Niri, and Combined profiles), the **first-boot welcome wizard** runs automatically. It guides you through:

- Terminal emulator selection  
- File manager selection  
- Font wizard (preset tiers)  
- Theme picker  
- Timezone/locale confirmation  
- Quick tips  

See [first-boot.md](first-boot.md) for details.

### Verify Installation

```bash
$ lintactl info
```

Expected output includes profile, theme, kernel, Btrfs status, and SELinux mode.

---

## Troubleshooting

- **Boot menu not showing USB:** Enable UEFI boot in firmware and disable any “legacy” or “CSM” mode.
- **Black screen after boot:** Try the `nomodeset` kernel option from the boot menu if you suspect a graphics issue.
- **Installation fails:** Ensure the target disk has enough space and that you selected the correct drive in the disk step.
