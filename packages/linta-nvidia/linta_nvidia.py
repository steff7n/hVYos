#!/usr/bin/env python3
"""linta-nvidia — NVIDIA GPU setup tool for Linta Linux.

Detects NVIDIA GPUs, installs appropriate proprietary drivers via
RPM Fusion + akmod, configures DKMS, Wayland compatibility, and
hybrid GPU switching.

Profiles: [KDE], [Niri], [Combined] (not relevant for [Bare])
Spec reference: README.md §9.2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

VERSION = "0.1.0"
RELEASE_FILE = Path("/etc/linta-release")

NVIDIA_ENV_CONF = Path("/etc/environment.d/10-linta-nvidia.conf")
MODPROBE_CONF = Path("/etc/modprobe.d/linta-nvidia.conf")
UDEV_RULES = Path("/etc/udev/rules.d/61-linta-nvidia-pm.rules")


@dataclass
class GpuInfo:
    pci_slot: str
    vendor: str
    model: str
    driver: str
    pci_id: str
    is_nvidia: bool = False


@dataclass
class NvidiaStatus:
    gpus: list[GpuInfo] = field(default_factory=list)
    driver_version: str = ""
    driver_package: str = ""
    is_hybrid: bool = False
    integrated_gpu: str = ""
    wayland_ready: bool = False
    profile: str = ""


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _require_root() -> None:
    if os.geteuid() != 0:
        print("Error: this command requires root privileges.")
        print("Run with: sudo linta-nvidia ...")
        sys.exit(1)


def _get_profile() -> str:
    if RELEASE_FILE.exists():
        for line in RELEASE_FILE.read_text().splitlines():
            if line.startswith("VARIANT_ID="):
                return line.split("=", 1)[1].strip().strip('"')
    return "unknown"


def detect_gpus() -> list[GpuInfo]:
    """Detect all GPUs using lspci."""
    gpus = []
    try:
        result = _run(["lspci", "-nn", "-D"])
    except FileNotFoundError:
        print("Warning: lspci not found. Install pciutils.")
        return gpus

    gpu_pattern = re.compile(
        r"^(\S+)\s+(VGA compatible controller|3D controller|Display controller):\s+(.+)$"
    )

    for line in result.stdout.splitlines():
        match = gpu_pattern.match(line)
        if not match:
            continue

        pci_slot = match.group(1)
        full_desc = match.group(3)

        pci_id_match = re.search(r"\[([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\]", full_desc)
        pci_id = pci_id_match.group(1) if pci_id_match else ""

        is_nvidia = "NVIDIA" in full_desc.upper()
        vendor = "NVIDIA" if is_nvidia else (
            "Intel" if "Intel" in full_desc else (
                "AMD" if "AMD" in full_desc or "ATI" in full_desc else "Unknown"
            )
        )

        driver = ""
        try:
            drv_result = _run(["lspci", "-k", "-s", pci_slot], check=False)
            for drv_line in drv_result.stdout.splitlines():
                if "Kernel driver in use:" in drv_line:
                    driver = drv_line.split(":", 1)[1].strip()
        except FileNotFoundError:
            pass

        model = re.sub(r"\s*\[[0-9a-fA-F:]+\]", "", full_desc).strip()

        gpus.append(GpuInfo(
            pci_slot=pci_slot,
            vendor=vendor,
            model=model,
            driver=driver,
            pci_id=pci_id,
            is_nvidia=is_nvidia,
        ))

    return gpus


def get_nvidia_driver_version() -> str:
    """Get installed NVIDIA driver version."""
    try:
        result = _run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                      check=False)
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except FileNotFoundError:
        pass

    modinfo = Path("/sys/module/nvidia/version")
    if modinfo.exists():
        return modinfo.read_text().strip()

    return ""


def get_status() -> NvidiaStatus:
    """Gather complete NVIDIA status."""
    status = NvidiaStatus()
    status.profile = _get_profile()
    status.gpus = detect_gpus()

    nvidia_gpus = [g for g in status.gpus if g.is_nvidia]
    non_nvidia_gpus = [g for g in status.gpus if not g.is_nvidia]

    status.is_hybrid = bool(nvidia_gpus) and bool(non_nvidia_gpus)
    if non_nvidia_gpus:
        status.integrated_gpu = non_nvidia_gpus[0].model

    status.driver_version = get_nvidia_driver_version()

    if status.driver_version:
        try:
            result = _run(["rpm", "-qa", "--qf", "%{NAME}\\n"], check=False)
            for pkg in result.stdout.splitlines():
                if "akmod-nvidia" in pkg or "kmod-nvidia" in pkg:
                    status.driver_package = pkg
                    break
        except FileNotFoundError:
            pass

    if nvidia_gpus and nvidia_gpus[0].driver == "nvidia":
        status.wayland_ready = NVIDIA_ENV_CONF.exists()

    return status


def _determine_driver_branch(gpus: list[GpuInfo]) -> str:
    """Determine which NVIDIA driver branch to install.

    Returns the akmod package name suffix: '' for latest, '470xx' for legacy, etc.
    """
    # For now, always use the latest driver branch.
    # Legacy GPU detection would require maintaining a PCI ID database.
    return ""


def _rpm_fusion_releasever() -> str:
    try:
        return _run(["rpm", "-E", "%fedora"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def cmd_status(args: argparse.Namespace) -> None:
    """Show NVIDIA GPU status."""
    status = get_status()

    nvidia_gpus = [g for g in status.gpus if g.is_nvidia]

    if not nvidia_gpus:
        print("  No NVIDIA GPU detected.")
        if status.gpus:
            print(f"  Found: {', '.join(g.model for g in status.gpus)}")
        return

    print(f"  NVIDIA GPU Setup — Linta ({status.profile})")
    print()

    for gpu in nvidia_gpus:
        print(f"  GPU:            {gpu.model}")
        print(f"  PCI:            {gpu.pci_slot}")
        print(f"  Kernel driver:  {gpu.driver or 'none (nouveau?)'}")

    print(f"  Driver version: {status.driver_version or 'not installed'}")
    if status.driver_package:
        print(f"  Driver package: {status.driver_package}")

    print(f"  Hybrid GPU:     {'yes' if status.is_hybrid else 'no'}")
    if status.is_hybrid:
        print(f"  Integrated:     {status.integrated_gpu}")

    wayland_label = "yes" if status.wayland_ready else "no (run: sudo linta-nvidia setup)"
    print(f"  Wayland ready:  {wayland_label}")

    if args.json:
        data = {
            "gpus": [{"model": g.model, "pci": g.pci_slot, "driver": g.driver,
                       "nvidia": g.is_nvidia} for g in status.gpus],
            "driver_version": status.driver_version,
            "driver_package": status.driver_package,
            "hybrid": status.is_hybrid,
            "integrated": status.integrated_gpu,
            "wayland_ready": status.wayland_ready,
            "profile": status.profile,
        }
        print(json.dumps(data, indent=2))


def cmd_setup(args: argparse.Namespace) -> None:
    """Full NVIDIA setup: driver install + Wayland config."""
    _require_root()

    gpus = detect_gpus()
    nvidia_gpus = [g for g in gpus if g.is_nvidia]

    if not nvidia_gpus:
        print("  No NVIDIA GPU detected. Nothing to do.")
        return

    print(f"  Detected NVIDIA GPU: {nvidia_gpus[0].model}")
    is_hybrid = any(not g.is_nvidia for g in gpus)

    # Step 1: Enable RPM Fusion
    print("\n  [1/5] Enabling RPM Fusion repositories...")
    _enable_rpm_fusion()

    # Step 2: Install akmod-nvidia
    branch = _determine_driver_branch(nvidia_gpus)
    pkg_name = f"akmod-nvidia{branch}" if not branch else f"akmod-nvidia-{branch}"
    if not branch:
        pkg_name = "akmod-nvidia"

    print(f"\n  [2/5] Installing {pkg_name}...")
    _install_driver(pkg_name)

    # Step 3: Configure Wayland
    print("\n  [3/5] Configuring Wayland compatibility...")
    _configure_wayland()

    # Step 4: Configure hybrid GPU (if applicable)
    if is_hybrid:
        print("\n  [4/5] Configuring hybrid GPU (PRIME)...")
        _configure_hybrid()
    else:
        print("\n  [4/5] Hybrid GPU: not applicable (single GPU)")

    # Step 5: Handle profile-specific quirks
    profile = _get_profile()
    print(f"\n  [5/5] Profile-specific setup ({profile})...")
    _configure_profile_quirks(profile)

    print("\n  Setup complete. Reboot to activate the NVIDIA driver.")
    print("  After reboot, verify with: linta-nvidia status")


def _enable_rpm_fusion() -> None:
    """Enable RPM Fusion free and nonfree repos."""
    try:
        result = _run(["rpm", "-qa", "rpmfusion-nonfree-release"], check=False)
        if "rpmfusion-nonfree-release" in result.stdout:
            print("    RPM Fusion already enabled.")
            return
    except FileNotFoundError:
        pass

    fedora_ver = _rpm_fusion_releasever()
    if not fedora_ver:
        print("    Error enabling RPM Fusion: could not determine Fedora release.")
        sys.exit(1)

    free_url = (
        f"https://mirrors.rpmfusion.org/free/fedora/"
        f"rpmfusion-free-release-{fedora_ver}.noarch.rpm"
    )
    nonfree_url = (
        f"https://mirrors.rpmfusion.org/nonfree/fedora/"
        f"rpmfusion-nonfree-release-{fedora_ver}.noarch.rpm"
    )

    try:
        _run(["dnf", "install", "-y", free_url, nonfree_url])
        print("    RPM Fusion enabled.")
    except subprocess.CalledProcessError as e:
        print(f"    Error enabling RPM Fusion: {e.stderr}")
        sys.exit(1)


def _install_driver(package: str) -> None:
    """Install NVIDIA driver package via DNF."""
    try:
        _run(["dnf", "install", "-y", package, "xorg-x11-drv-nvidia-cuda"])
        print(f"    {package} installed.")
    except subprocess.CalledProcessError as e:
        print(f"    Error installing driver: {e.stderr}")
        sys.exit(1)

    # Wait for akmod to build
    print("    Building kernel module (this may take a few minutes)...")
    try:
        _run(["akmods", "--force"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("    Warning: akmods not available; module will build on next boot.")


def _configure_wayland() -> None:
    """Set environment variables for NVIDIA Wayland support."""
    env_vars = {
        "GBM_BACKEND": "nvidia-drm",
        "LIBVA_DRIVER_NAME": "nvidia",
        "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
        "WLR_NO_HARDWARE_CURSORS": "1",
        "MOZ_ENABLE_WAYLAND": "1",
    }

    lines = [f"{k}={v}" for k, v in env_vars.items()]
    NVIDIA_ENV_CONF.parent.mkdir(parents=True, exist_ok=True)
    NVIDIA_ENV_CONF.write_text("\n".join(lines) + "\n")
    print(f"    Environment variables written to {NVIDIA_ENV_CONF}")

    # Enable nvidia-drm modeset
    MODPROBE_CONF.parent.mkdir(parents=True, exist_ok=True)
    MODPROBE_CONF.write_text(
        "options nvidia-drm modeset=1 fbdev=1\n"
        "options nvidia NVreg_PreserveVideoMemoryAllocations=1\n"
    )
    print(f"    Modprobe config written to {MODPROBE_CONF}")

    # Enable nvidia systemd services for suspend/resume
    for svc in ["nvidia-suspend", "nvidia-hibernate", "nvidia-resume"]:
        try:
            _run(["systemctl", "enable", f"{svc}.service"], check=False)
        except FileNotFoundError:
            pass

    # Rebuild initramfs with nvidia modules
    try:
        _run(["dracut", "--force"])
        print("    Initramfs rebuilt.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("    Warning: could not rebuild initramfs.")


def _configure_hybrid() -> None:
    """Configure PRIME offloading for hybrid GPU laptops."""
    # Create prime-run wrapper
    prime_run = Path("/usr/local/bin/prime-run")
    prime_run.write_text(
        "#!/bin/bash\n"
        'export __NV_PRIME_RENDER_OFFLOAD=1\n'
        'export __NV_PRIME_RENDER_OFFLOAD_PROVIDER=NVIDIA-G0\n'
        'export __GLX_VENDOR_LIBRARY_NAME=nvidia\n'
        'export __VK_LAYER_NV_optimus=NVIDIA_only\n'
        'exec "$@"\n'
    )
    prime_run.chmod(0o755)
    print(f"    prime-run wrapper created at {prime_run}")
    print("    Usage: prime-run <application> — forces NVIDIA GPU for that app")

    # NVIDIA power management udev rules
    UDEV_RULES.parent.mkdir(parents=True, exist_ok=True)
    UDEV_RULES.write_text(
        '# Enable runtime PM for NVIDIA GPU\n'
        'ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", '
        'ATTR{class}=="0x030000", TEST=="power/control", '
        'ATTR{power/control}="auto"\n'
        'ACTION=="bind", SUBSYSTEM=="pci", ATTR{vendor}=="0x10de", '
        'ATTR{class}=="0x030200", TEST=="power/control", '
        'ATTR{power/control}="auto"\n'
    )
    print(f"    Power management udev rules written to {UDEV_RULES}")


def _configure_profile_quirks(profile: str) -> None:
    """Handle profile-specific NVIDIA configuration."""
    if profile in ("kde", "combined"):
        # KDE/Xwayland: ensure proper NVIDIA Xwayland support
        kwin_env = Path("/etc/environment.d/11-linta-kwin-nvidia.conf")
        kwin_env.write_text(
            "KWIN_DRM_USE_EGL_STREAMS=0\n"
        )
        print(f"    KDE Wayland NVIDIA config written to {kwin_env}")

    if profile in ("niri", "combined"):
        print("    Niri: no Xwayland — NVIDIA GBM backend is sufficient.")

    if profile == "bare":
        print("    Bare profile: NVIDIA driver installed for compute/TTY use.")


def cmd_uninstall(args: argparse.Namespace) -> None:
    """Remove NVIDIA proprietary driver and restore nouveau."""
    _require_root()

    print("  Removing NVIDIA proprietary driver...")

    try:
        _run(["dnf", "remove", "-y", "akmod-nvidia*", "xorg-x11-drv-nvidia*",
              "nvidia-gpu-firmware"])
    except subprocess.CalledProcessError:
        print("  Warning: some packages may not have been installed.")

    # Remove config files
    for f in [NVIDIA_ENV_CONF, MODPROBE_CONF, UDEV_RULES]:
        if f.exists():
            f.unlink()

    kwin_env = Path("/etc/environment.d/11-linta-kwin-nvidia.conf")
    if kwin_env.exists():
        kwin_env.unlink()

    prime_run = Path("/usr/local/bin/prime-run")
    if prime_run.exists():
        prime_run.unlink()

    try:
        _run(["dracut", "--force"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    print("  NVIDIA driver removed. Reboot to use nouveau.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linta-nvidia",
        description="NVIDIA GPU setup tool for Linta Linux",
    )
    parser.add_argument("--version", action="version", version=f"linta-nvidia {VERSION}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    p_status = sub.add_parser("status", help="Show NVIDIA GPU status")
    p_status.add_argument("--json", action="store_true", help="JSON output")
    p_status.set_defaults(func=cmd_status)

    p_setup = sub.add_parser("setup", help="Install and configure NVIDIA driver")
    p_setup.set_defaults(func=cmd_setup)

    p_uninstall = sub.add_parser("uninstall", help="Remove NVIDIA driver, restore nouveau")
    p_uninstall.set_defaults(func=cmd_uninstall)

    return parser


def main() -> NoReturn:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)
    sys.exit(0)


if __name__ == "__main__":
    main()
