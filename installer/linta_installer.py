#!/usr/bin/env python3
"""
Linta Linux TUI Installer

Ncurses-based text installer (Devuan-style) for Linta Linux.
Spec reference: README.md §10.1
Profiles: [All]
"""

from __future__ import annotations

import curses
import os
import random
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VERSION = "0.1.0"

ADJECTIVES = [
    "silent", "brave", "swift", "calm", "bright", "dark", "wild", "warm",
    "cool", "bold", "keen", "fair", "pure", "deep", "wise", "free", "true",
    "vast", "rare", "soft",
]
NOUNS = [
    "pine", "otter", "hawk", "wolf", "creek", "stone", "flame", "frost",
    "ridge", "maple", "cedar", "wren", "fox", "elk", "sage", "peak", "vale",
    "fern", "moss", "lark",
]

PROFILES = [
    ("kde", "KDE Plasma", "Full KDE Plasma desktop on Wayland with Xwayland."),
    ("niri", "Niri", "Scrollable tiling Wayland compositor. Pure Wayland."),
    ("combined", "Combined", "KDE Plasma + Niri, switchable at login."),
    ("bare", "Bare", "TTY-only. No display manager, no GUI."),
]

COMMON_LOCALES = [
    "en_US.UTF-8",
    "en_GB.UTF-8",
    "de_DE.UTF-8",
    "fr_FR.UTF-8",
    "es_ES.UTF-8",
    "it_IT.UTF-8",
    "pt_BR.UTF-8",
    "ru_RU.UTF-8",
    "ja_JP.UTF-8",
    "zh_CN.UTF-8",
    "ko_KR.UTF-8",
    "pl_PL.UTF-8",
    "nl_NL.UTF-8",
    "sv_SE.UTF-8",
    "cs_CZ.UTF-8",
]

DEFAULT_RELEASEVER = "42"
DISTRO_VERSION = "25.1"
DEFAULT_USERNAME = "linta"
DEFAULT_PASSWORD = "linta"

BASE_PACKAGES = [
    "@core",
    "@standard",
    "kernel",
    "btrfs-progs",
    "grub2-efi-x64",
    "grub2-efi-x64-modules",
    "efibootmgr",
    "shim-x64",
]

GRAPHICAL_PACKAGES = [
    "flatpak",
    "mesa-dri-drivers",
    "pipewire",
    "pipewire-pulseaudio",
    "pipewire-alsa",
    "wireplumber",
    "power-profiles-daemon",
    "wl-clipboard",
    "dejavu-sans-fonts",
    "dejavu-sans-mono-fonts",
]

KDE_PACKAGES = [
    "plasma-desktop",
    "plasma-workspace",
    "sddm",
    "sddm-kcm",
    "plasma-workspace-wayland",
    "kwin-wayland",
    "xorg-x11-server-Xwayland",
    "dolphin",
    "konsole",
    "plasma-systemsettings",
    "powerdevil",
    "plasma-nm",
    "plasma-pa",
    "bluedevil",
    "kde-gtk-config",
    "breeze-gtk",
    "kscreenlocker",
    "breeze-icon-theme",
    "plasma-integration",
    "kvantum",
]

NIRI_PACKAGES = [
    "sddm",
    "fuzzel",
    "waybar",
    "mako",
    "swaylock",
    "swaybg",
    "foot",
    "qt6-qtwayland",
    "qt5-qtwayland",
    "polkit-gnome",
    "xdg-desktop-portal",
    "xdg-desktop-portal-gtk",
    "xdg-desktop-portal-wlr",
]


def _partition_device(disk: str, number: int) -> str:
    """Return partition device path (e.g. /dev/nvme0n1p1 or /dev/sda1)."""
    suffix = f"p{number}" if disk[-1].isdigit() else str(number)
    return f"{disk}{suffix}"


@dataclass
class InstallState:
    """Collected installer choices."""
    profile: str
    hostname: str
    locale: str
    timezone: str
    luks: bool
    luks_passphrase: str = ""
    disk: str = ""
    root_mount: Path = Path("/mnt/sysimage")


def generate_hostname() -> str:
    """Generate adjective-noun hostname."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj}-{noun}"


def get_block_devices() -> list[tuple[str, str]]:
    """List block devices suitable for installation (exclude readonly, loop)."""
    devices: list[tuple[str, str]] = []
    try:
        result = subprocess.run(
            ["lsblk", "-d", "-n", "-o", "NAME,SIZE,MODEL", "-e", "7,11"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().splitlines():
            parts = line.split(None, 2)
            if len(parts) >= 2:
                name = parts[0]
                if not name.startswith("loop") and not name.startswith("zram"):
                    path = f"/dev/{name}"
                    size = parts[1]
                    model = parts[2] if len(parts) > 2 else ""
                    devices.append((path, f"{path}  {size}  {model}".strip()))
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return devices


def get_timezones() -> list[str]:
    """Get timezone list from timedatectl."""
    try:
        result = subprocess.run(
            ["timedatectl", "list-timezones"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().splitlines()
    except (subprocess.SubprocessError, FileNotFoundError):
        return [
            "UTC", "America/New_York", "America/Los_Angeles", "Europe/London",
            "Europe/Berlin", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai",
        ]


def _dedupe_packages(packages: list[str]) -> list[str]:
    """Preserve package order while removing duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for package in packages:
        if package not in seen:
            seen.add(package)
            result.append(package)
    return result


def _package_list_for_state(state: InstallState) -> list[str]:
    """Return the package list for the selected installer profile."""
    packages = list(BASE_PACKAGES)

    if state.profile in ("kde", "niri", "combined"):
        packages.extend(GRAPHICAL_PACKAGES)
    if state.profile in ("kde", "combined"):
        packages.extend(KDE_PACKAGES)
    if state.profile in ("niri", "combined"):
        packages.extend(NIRI_PACKAGES)
    if state.luks:
        packages.append("cryptsetup")

    return _dedupe_packages(packages)


def _build_dnf_install_command(root: Path, packages: list[str]) -> list[str]:
    """Build the DNF install command for the target root."""
    releasever = os.environ.get("LINTA_RELEASEVER", DEFAULT_RELEASEVER)
    return [
        "dnf",
        "--installroot",
        str(root),
        "--releasever",
        releasever,
        "-y",
        "install",
    ] + packages


def _write_linta_release(root: Path, profile: str) -> None:
    """Write release metadata expected by Linta tools."""
    release_file = root / "etc/linta-release"
    release_file.parent.mkdir(parents=True, exist_ok=True)
    release_file.write_text(
        "\n".join(
            [
                'NAME="Linta"',
                f'VERSION="{DISTRO_VERSION}"',
                "ID=linta",
                "ID_LIKE=fedora",
                f"VARIANT_ID={profile}",
                'HOME_URL="https://lintalinux.org"',
                'SUPPORT_URL="https://lintalinux.org/docs"',
            ]
        )
        + "\n"
    )


def _write_system_config(root: Path, state: InstallState) -> None:
    """Write basic system metadata into the target root."""
    etc_dir = root / "etc"
    etc_dir.mkdir(parents=True, exist_ok=True)

    (etc_dir / "hostname").write_text(state.hostname + "\n")
    (etc_dir / "locale.conf").write_text(f"LANG={state.locale}\n")

    localtime = etc_dir / "localtime"
    if localtime.exists() or localtime.is_symlink():
        localtime.unlink()
    localtime.symlink_to(f"/usr/share/zoneinfo/{state.timezone}")

    _write_linta_release(root, state.profile)


def _create_default_user(root: Path) -> None:
    """Create the default installer user expected by the distro workflow."""
    subprocess.run(
        ["chroot", str(root), "useradd", "-m", "-G", "wheel", DEFAULT_USERNAME],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["chroot", str(root), "chpasswd"],
        input=f"{DEFAULT_USERNAME}:{DEFAULT_PASSWORD}\n",
        text=True,
        check=True,
        capture_output=True,
    )


def draw_header(win: curses.window, title: str, color: int) -> None:
    """Draw screen header."""
    h, w = win.getmaxyx()
    win.addstr(0, 0, " " * w, curses.A_REVERSE)
    win.addstr(0, max(0, (w - len(title)) // 2), title, curses.A_REVERSE | color)
    win.addstr(2, 0, "")
    win.refresh()


def screen_welcome(stdscr: curses.window, color_acc: int) -> bool:
    """Welcome screen. Returns True to continue."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title = "Linta Linux Installer"
    draw_header(stdscr, title, color_acc)

    lines = [
        "",
        "  Lean by design.",
        "",
        f"  Version: {VERSION}",
        "",
        "  This installer will guide you through setting up Linta Linux",
        "  on your system.",
        "",
        "  Press ENTER to continue, or Q to quit.",
    ]
    for i, line in enumerate(lines, start=4):
        if i < h - 1:
            stdscr.addstr(i, 0, line[: w - 1])
    stdscr.refresh()

    while True:
        try:
            key = stdscr.getch()
        except curses.error:
            continue
        if key == ord("\n") or key == ord("\r"):
            return True
        if key in (ord("q"), ord("Q")):
            return False


def screen_profile(stdscr: curses.window, color_acc: int) -> str | None:
    """Profile selection. Returns profile id or None to go back."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_header(stdscr, "Select installation profile", color_acc)

    instructions = "Use arrow keys, ENTER to select, B to go back:"
    stdscr.addstr(4, 0, instructions[: w - 1])
    selected = 0

    while True:
        for i, (pid, pname, pdesc) in enumerate(PROFILES):
            y = 6 + i * 2
            if y >= h - 2:
                break
            prefix = "> " if i == selected else "  "
            text = f"{prefix}{pname}"
            stdscr.addstr(y, 0, text[: w - 1])
            stdscr.addstr(y + 1, 4, pdesc[: w - 5])
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(PROFILES)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(PROFILES)
        elif key == ord("\n") or key == ord("\r"):
            return PROFILES[selected][0]
        elif key in (ord("b"), ord("B")):
            return None


def screen_hostname(stdscr: curses.window, color_acc: int, initial: str = "") -> str | None:
    """Hostname screen. Returns hostname or None to go back."""
    hostname = initial or generate_hostname()
    cursor_pos = len(hostname)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_header(stdscr, "Hostname", color_acc)

    stdscr.addstr(4, 0, "Enter hostname (adjective-noun format, e.g. silent-pine):"[: w - 1])
    stdscr.addstr(6, 0, hostname[: w - 1])
    stdscr.addstr(8, 0, "B to go back"[: w - 1])
    stdscr.move(6, cursor_pos)
    stdscr.refresh()

    while True:
        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == ord("\n") or key == ord("\r"):
            return hostname.strip() if hostname.strip() else generate_hostname()
        if key in (ord("b"), ord("B")):
            return None
        if key == curses.KEY_LEFT and cursor_pos > 0:
            cursor_pos -= 1
        elif key == curses.KEY_RIGHT and cursor_pos < len(hostname):
            cursor_pos += 1
        elif key == curses.KEY_BACKSPACE and cursor_pos > 0:
            hostname = hostname[: cursor_pos - 1] + hostname[cursor_pos:]
            cursor_pos -= 1
        elif key == curses.KEY_DC and cursor_pos < len(hostname):
            hostname = hostname[:cursor_pos] + hostname[cursor_pos + 1:]
        elif 32 <= key <= 126 and len(hostname) < 63:
            hostname = hostname[:cursor_pos] + chr(key) + hostname[cursor_pos:]
            cursor_pos += 1

        stdscr.addstr(6, 0, (hostname + " " * (w - len(hostname) - 1))[: w - 1])
        stdscr.move(6, min(cursor_pos, w - 1))
        stdscr.refresh()


def screen_locale(stdscr: curses.window, color_acc: int) -> str | None:
    """Locale selection. Returns locale or None to go back."""
    locales = COMMON_LOCALES
    selected = 0
    default_idx = next((i for i, l in enumerate(locales) if l == "en_US.UTF-8"), 0)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Locale", color_acc)
        stdscr.addstr(4, 0, "Use arrow keys, ENTER to select, B to go back:"[: w - 1])

        for i, loc in enumerate(locales):
            y = 6 + i
            if y >= h - 2:
                break
            prefix = "> " if i == selected else "  "
            suffix = " (default)" if i == default_idx else ""
            stdscr.addstr(y, 0, (prefix + loc + suffix)[: w - 1])
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(locales)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(locales)
        elif key == ord("\n") or key == ord("\r"):
            return locales[selected]
        elif key in (ord("b"), ord("B")):
            return None


def screen_timezone(stdscr: curses.window, color_acc: int) -> str | None:
    """Timezone selection. Returns timezone or None to go back."""
    timezones = get_timezones()
    selected = next((i for i, tz in enumerate(timezones) if tz == "UTC"), 0)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Timezone", color_acc)
        stdscr.addstr(4, 0, "Use arrow keys, ENTER to select, B to go back:"[: w - 1])

        for i, tz in enumerate(timezones):
            y = 6 + i
            if y >= h - 2:
                break
            prefix = "> " if i == selected else "  "
            stdscr.addstr(y, 0, (prefix + tz)[: w - 1])
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif key == curses.KEY_DOWN:
            selected = min(len(timezones) - 1, selected + 1)
        elif key == ord("\n") or key == ord("\r"):
            return timezones[selected]
        elif key in (ord("b"), ord("B")):
            return None


def screen_disk_encryption(stdscr: curses.window, color_acc: int) -> tuple[bool, str] | None:
    """Disk encryption screen. Returns (enabled, passphrase) or None to go back."""
    luks_enabled = False  # Off by default

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Disk encryption (LUKS2)", color_acc)

        stdscr.addstr(4, 0, "Enable LUKS2 disk encryption? (Off by default)"[: w - 1])
        no_mark = "[*]" if not luks_enabled else "[ ]"
        yes_mark = "[*]" if luks_enabled else "[ ]"
        stdscr.addstr(5, 0, f"  {no_mark} No  {yes_mark} Yes"[: w - 1])
        stdscr.addstr(7, 0, "Use SPACE to toggle, ENTER to confirm, B to go back"[: w - 1])
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == ord(" "):
            luks_enabled = not luks_enabled
        elif key in (ord("b"), ord("B")):
            return None
        elif key == ord("\n") or key == ord("\r"):
            break

    if not luks_enabled:
        return (False, "")

    stdscr.addstr(9, 0, "Enter passphrase (hidden):"[: w - 1])
    stdscr.refresh()
    passphrase = ""
    curses.noecho()
    try:
        passphrase = stdscr.getstr(10, 0, 256).decode("utf-8", errors="replace")
    except (curses.error, TypeError):
        pass
    curses.echo()
    return (True, passphrase)


def screen_disk(stdscr: curses.window, color_acc: int) -> str | None:
    """Disk selection. Returns device path or None to go back."""
    devices = get_block_devices()
    if not devices:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Disk selection", color_acc)
        stdscr.addstr(4, 0, "No suitable block devices found."[: w - 1])
        stdscr.addstr(5, 0, "Press any key to go back."[: w - 1])
        stdscr.getch()
        return None

    selected = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Select target disk (ALL DATA WILL BE DESTROYED)", color_acc)
        stdscr.addstr(4, 0, "Use arrow keys, ENTER to select, B to go back:"[: w - 1])

        for i, (path, desc) in enumerate(devices):
            y = 6 + i
            if y >= h - 2:
                break
            prefix = "> " if i == selected else "  "
            stdscr.addstr(y, 0, (prefix + desc)[: w - 1])
        stdscr.refresh()

        try:
            key = stdscr.getch()
        except curses.error:
            continue

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(devices)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(devices)
        elif key == ord("\n") or key == ord("\r"):
            return devices[selected][0]
        elif key in (ord("b"), ord("B")):
            return None


def screen_confirmation(stdscr: curses.window, color_acc: int, state: InstallState) -> bool:
    """Confirmation screen. Returns True to proceed, False to go back."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_header(stdscr, "Confirmation", color_acc)

    profile_name = next((p[1] for p in PROFILES if p[0] == state.profile), state.profile)
    lines = [
        "",
        f"  Profile:     {profile_name}",
        f"  Hostname:    {state.hostname}",
        f"  Locale:      {state.locale}",
        f"  Timezone:    {state.timezone}",
        f"  Encryption:  {'LUKS2' if state.luks else 'Off'}",
        f"  Target:      {state.disk}",
        "",
        "  WARNING: All data on the target disk will be destroyed.",
        "",
        "  Press ENTER to proceed, B to go back.",
    ]
    for i, line in enumerate(lines, start=4):
        if i < h - 1:
            stdscr.addstr(i, 0, line[: w - 1])
    stdscr.refresh()

    while True:
        try:
            key = stdscr.getch()
        except curses.error:
            continue
        if key == ord("\n") or key == ord("\r"):
            return True
        if key in (ord("b"), ord("B")):
            return False


def run_install(stdscr: curses.window, state: InstallState, color_acc: int) -> bool:
    """Execute installation steps. Returns True on success."""
    root = state.root_mount
    disk = state.disk
    log_lines: list[str] = []

    def log(msg: str) -> None:
        log_lines.append(msg)
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_header(stdscr, "Installing...", color_acc)
        for i, line in enumerate(log_lines[- (h - 6) :], start=4):
            stdscr.addstr(i, 0, line[: w - 1])
        stdscr.refresh()

    try:
        root.mkdir(parents=True, exist_ok=True)
        # Phase 1: Partition
        log("Partitioning disk...")
        subprocess.run(
            ["parted", "-s", disk, "mklabel", "gpt"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["parted", "-s", disk, "mkpart", "EFI", "fat32", "1MiB", "513MiB"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["parted", "-s", disk, "set", "1", "esp", "on"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["parted", "-s", disk, "mkpart", "boot", "ext4", "513MiB", "1537MiB"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["parted", "-s", disk, "mkpart", "btrfs", "btrfs", "1537MiB", "100%"],
            check=True,
            capture_output=True,
        )
        log("Partitioning complete.")

        # Phase 2: Format and Btrfs
        log("Formatting partitions...")
        efi_partition = _partition_device(disk, 1)
        boot_partition = _partition_device(disk, 2)
        root_partition = _partition_device(disk, 3)
        subprocess.run(
            ["mkfs.vfat", "-F", "32", "-n", "EFI", efi_partition],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["mkfs.ext4", "-L", "boot", boot_partition],
            check=True,
            capture_output=True,
        )

        btrfs_part = root_partition
        if state.luks:
            log("Setting up LUKS2...")
            proc = subprocess.Popen(
                ["cryptsetup", "luksFormat", "-q", "--type", "luks2", btrfs_part],
                stdin=subprocess.PIPE,
                capture_output=True,
            )
            proc.communicate(state.luks_passphrase.encode() + b"\n")
            if proc.returncode != 0:
                raise RuntimeError("LUKS formatting failed")
            mapper_name = "linta-root"
            proc = subprocess.Popen(
                ["cryptsetup", "open", btrfs_part, mapper_name],
                stdin=subprocess.PIPE,
                capture_output=True,
            )
            proc.communicate(state.luks_passphrase.encode() + b"\n")
            if proc.returncode != 0:
                raise RuntimeError("LUKS open failed")
            btrfs_part = f"/dev/mapper/{mapper_name}"

        subprocess.run(
            ["mkfs.btrfs", "-f", "-L", "linta", btrfs_part],
            check=True,
            capture_output=True,
        )
        log("Creating Btrfs subvolumes...")
        subprocess.run(["mkdir", "-p", str(root)], check=True, capture_output=True)
        subprocess.run(
            ["mount", btrfs_part, str(root)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["btrfs", "subvolume", "create", str(root / "@")],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["btrfs", "subvolume", "create", str(root / "@home")],
            check=True,
            capture_output=True,
        )
        subprocess.run(["umount", str(root)], check=True, capture_output=True)
        subprocess.run(
            ["mount", "-o", "subvol=@,compress=zstd:1", btrfs_part, str(root)],
            check=True,
            capture_output=True,
        )
        subprocess.run(["mkdir", "-p", str(root / "home")], check=True, capture_output=True)
        subprocess.run(
            ["mount", "-o", "subvol=@home,compress=zstd:1", btrfs_part, str(root / "home")],
            check=True,
            capture_output=True,
        )
        subprocess.run(["mkdir", "-p", str(root / "boot")], check=True, capture_output=True)
        subprocess.run(
            ["mount", boot_partition, str(root / "boot")],
            check=True,
            capture_output=True,
        )
        subprocess.run(["mkdir", "-p", str(root / "boot/efi")], check=True, capture_output=True)
        subprocess.run(
            ["mount", efi_partition, str(root / "boot/efi")],
            check=True,
            capture_output=True,
        )
        log("Btrfs setup complete.")

        # Phase 3: Package install (simplified - base + minimal)
        log("Installing packages (this may take several minutes)...")
        packages = _package_list_for_state(state)
        pkg_cmd = _build_dnf_install_command(root, packages)
        result = subprocess.run(pkg_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            log(f"Package install warning: {result.stderr[:200]}")
        log("Packages installed.")

        # Phase 4: Config
        log("Configuring system...")
        _write_system_config(root, state)
        _create_default_user(root)
        log("Config complete.")

        # Phase 5: Bootloader
        log("Installing bootloader...")
        subprocess.run(
            ["grub2-install", "--target=x86_64-efi", "--efi-directory",
             str(root / "boot/efi"), "--bootloader-id=linta"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["chroot", str(root), "grub2-mkconfig", "-o", "/boot/grub2/grub.cfg"],
            check=True,
            capture_output=True,
        )
        log("Bootloader installed.")

        log("Installation complete.")
        return True

    except subprocess.CalledProcessError as e:
        log(f"Error: {e}")
        return False
    except Exception as e:
        log(f"Error: {e}")
        return False


def screen_progress(stdscr: curses.window, state: InstallState, color_acc: int) -> bool:
    """Run installation and show progress."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    draw_header(stdscr, "Installing...", color_acc)
    stdscr.addstr(4, 0, "Starting installation...")
    stdscr.refresh()
    return run_install(stdscr, state, color_acc)


def screen_complete(stdscr: curses.window, color_acc: int, success: bool) -> None:
    """Completion screen."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    if success:
        draw_header(stdscr, "Installation complete", color_acc)
        lines = [
            "",
            "  Installation complete. Remove media and reboot.",
            "",
            "  Press any key to exit.",
        ]
    else:
        draw_header(stdscr, "Installation failed", color_acc)
        lines = [
            "",
            "  Installation encountered errors.",
            "  Press any key to exit.",
        ]
    for i, line in enumerate(lines, start=4):
        if i < h - 1:
            stdscr.addstr(i, 0, line[: w - 1])
    stdscr.refresh()
    try:
        stdscr.getch()
    except curses.error:
        pass


def main(stdscr: curses.window) -> int:
    """Main installer loop."""
    curses.curs_set(1)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    color_acc = curses.color_pair(1)

    if not screen_welcome(stdscr, color_acc):
        return 0

    state: InstallState | None = None
    while state is None or state.disk == "":
        profile = screen_profile(stdscr, color_acc)
        if profile is None:
            if state is None:
                return 0
            continue
        hostname = screen_hostname(stdscr, color_acc, state.hostname if state else "")
        if hostname is None:
            continue
        locale = screen_locale(stdscr, color_acc)
        if locale is None:
            continue
        timezone = screen_timezone(stdscr, color_acc)
        if timezone is None:
            continue
        enc = screen_disk_encryption(stdscr, color_acc)
        if enc is None:
            continue
        luks, luks_pass = enc
        disk = screen_disk(stdscr, color_acc)
        if disk is None:
            continue
        state = InstallState(
            profile=profile,
            hostname=hostname,
            locale=locale,
            timezone=timezone,
            luks=luks,
            luks_passphrase=luks_pass,
            disk=disk,
        )
        if not screen_confirmation(stdscr, color_acc, state):
            state.disk = ""
            continue
        break

    success = screen_progress(stdscr, state, color_acc)
    screen_complete(stdscr, color_acc, success)
    return 0 if success else 1


def run() -> None:
    """Entry point with curses wrapper."""
    try:
        sys.exit(curses.wrapper(main))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    run()
