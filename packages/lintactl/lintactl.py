#!/usr/bin/env python3
"""lintactl — Linta Linux system management tool.

Handles distro-specific features only. Does NOT wrap standard tools
(dnf, btrfs, systemctl). See README.md §9.1.

Profiles: [All]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

VERSION = "0.1.0"
RELEASE_FILE = Path("/etc/linta-release")
THEMES_DIR = Path("/usr/share/linta/themes")
ACTIVE_THEME_FILE = Path("/etc/linta/active-theme")


def _read_release() -> dict[str, str]:
    """Parse /etc/linta-release into a dict."""
    data: dict[str, str] = {}
    if not RELEASE_FILE.exists():
        return data
    for line in RELEASE_FILE.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            data[key.strip()] = value.strip().strip('"')
    return data


def _get_profile() -> str:
    release = _read_release()
    return release.get("VARIANT_ID", "unknown")


def _get_active_theme() -> str:
    if ACTIVE_THEME_FILE.exists():
        return ACTIVE_THEME_FILE.read_text().strip()
    profile = _get_profile()
    if profile == "kde":
        return "linta-kde-default"
    elif profile in ("niri", "combined"):
        return "linta-niri-rice1"
    return "none"


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


# --- Subcommands ---


def cmd_info(args: argparse.Namespace) -> None:
    """Display Linta system information."""
    release = _read_release()
    profile = _get_profile()
    theme = _get_active_theme()

    kernel = "unknown"
    try:
        kernel = _run(["uname", "-r"]).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    btrfs_status = "unknown"
    try:
        result = _run(["findmnt", "-n", "-o", "FSTYPE", "/"])
        btrfs_status = "active" if result.stdout.strip() == "btrfs" else result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    selinux = "unknown"
    try:
        selinux = _run(["getenforce"], check=False).stdout.strip()
    except FileNotFoundError:
        pass

    print(f"  Linta {release.get('VERSION', 'dev')}")
    print(f"  Profile:    {profile}")
    print(f"  Theme:      {theme}")
    print(f"  Kernel:     {kernel}")
    print(f"  Filesystem: Btrfs ({btrfs_status})")
    print(f"  SELinux:    {selinux}")

    if args.json:
        data = {
            "name": release.get("NAME", "Linta"),
            "version": release.get("VERSION", "dev"),
            "profile": profile,
            "theme": theme,
            "kernel": kernel,
            "btrfs": btrfs_status,
            "selinux": selinux,
        }
        print(json.dumps(data, indent=2))


def cmd_profile(args: argparse.Namespace) -> None:
    """Show current installation profile."""
    profile = _get_profile()
    profiles_info = {
        "kde": "KDE Plasma (Wayland + Xwayland)",
        "niri": "Niri (pure Wayland, scrollable tiling)",
        "combined": "Combined (KDE + Niri, switchable via SDDM)",
        "bare": "Bare (TTY-only, no graphical environment)",
    }
    desc = profiles_info.get(profile, "Unknown profile")
    print(f"  Profile: {profile}")
    print(f"  {desc}")


def cmd_theme_list(args: argparse.Namespace) -> None:
    """List available themes."""
    active = _get_active_theme()
    profile = _get_profile()

    if not THEMES_DIR.exists():
        print("  No themes installed.")
        print(f"  Themes directory: {THEMES_DIR}")
        return

    themes = sorted(d.name for d in THEMES_DIR.iterdir() if d.is_dir())
    if not themes:
        print("  No themes found.")
        return

    print("  Available themes:")
    for t in themes:
        marker = " *" if t == active else ""
        meta_file = THEMES_DIR / t / "metadata.json"
        desc = ""
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                desc = f" — {meta.get('description', '')}"
                target = meta.get("profile", "")
                if target and target != profile and target != "all":
                    desc += f" [requires {target} profile]"
            except (json.JSONDecodeError, OSError):
                pass
        print(f"    {t}{marker}{desc}")


def cmd_theme_set(args: argparse.Namespace) -> None:
    """Switch the active theme."""
    theme_name = args.name
    theme_dir = THEMES_DIR / theme_name

    if not theme_dir.exists():
        print(f"  Error: theme '{theme_name}' not found.")
        print(f"  Run 'lintactl theme list' to see available themes.")
        sys.exit(1)

    apply_script = theme_dir / "apply.sh"
    if not apply_script.exists():
        print(f"  Error: theme '{theme_name}' has no apply.sh script.")
        sys.exit(1)

    print(f"  Applying theme '{theme_name}'...")
    try:
        result = _run(["bash", str(apply_script)])
        if result.stdout.strip():
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"  Error applying theme: {e.stderr}")
        sys.exit(1)

    ACTIVE_THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_THEME_FILE.write_text(theme_name + "\n")
    print(f"  Theme set to '{theme_name}'.")


def cmd_nvidia(args: argparse.Namespace) -> None:
    """Invoke NVIDIA setup tool."""
    try:
        os.execvp("linta-nvidia", ["linta-nvidia"] + args.nvidia_args)
    except FileNotFoundError:
        print("  Error: linta-nvidia is not installed.")
        print("  Install it with: sudo dnf install linta-nvidia")
        sys.exit(1)


def cmd_font_wizard(args: argparse.Namespace) -> None:
    """Re-run the font wizard from first-boot setup."""
    try:
        os.execvp("linta-welcome", ["linta-welcome", "--font-wizard-only"])
    except FileNotFoundError:
        print("  Error: linta-welcome is not installed.")
        print("  Install it with: sudo dnf install linta-welcome")
        sys.exit(1)


def cmd_snapshot(args: argparse.Namespace) -> None:
    """Invoke snapshot management tool."""
    try:
        os.execvp("linta-snapshots", ["linta-snapshots"] + args.snapshot_args)
    except FileNotFoundError:
        print("  Error: linta-snapshots is not installed.")
        print("  Install it with: sudo dnf install linta-snapshots")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lintactl",
        description="Linta Linux system management tool",
    )
    parser.add_argument(
        "--version", action="version", version=f"lintactl {VERSION}"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # info
    p_info = sub.add_parser("info", help="Display system information")
    p_info.add_argument("--json", action="store_true", help="Output as JSON")
    p_info.set_defaults(func=cmd_info)

    # profile
    p_profile = sub.add_parser("profile", help="Show current profile")
    p_profile.set_defaults(func=cmd_profile)

    # theme
    p_theme = sub.add_parser("theme", help="Theme management")
    theme_sub = p_theme.add_subparsers(dest="theme_command")

    p_theme_list = theme_sub.add_parser("list", help="List available themes")
    p_theme_list.set_defaults(func=cmd_theme_list)

    p_theme_set = theme_sub.add_parser("set", help="Set active theme")
    p_theme_set.add_argument("name", help="Theme name to activate")
    p_theme_set.set_defaults(func=cmd_theme_set)

    # nvidia
    p_nvidia = sub.add_parser("nvidia", help="NVIDIA GPU setup")
    p_nvidia.add_argument("nvidia_args", nargs="*", default=[])
    p_nvidia.set_defaults(func=cmd_nvidia)

    # font-wizard
    p_font = sub.add_parser("font-wizard", help="Re-run font selection wizard")
    p_font.set_defaults(func=cmd_font_wizard)

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Btrfs snapshot management")
    p_snap.add_argument("snapshot_args", nargs="*", default=[])
    p_snap.set_defaults(func=cmd_snapshot)

    return parser


def main() -> NoReturn:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        # theme subparser needs special handling
        if args.command == "theme" and not hasattr(args, "theme_command"):
            sub = [a for a in parser._subparsers._actions if isinstance(a, argparse._SubParsersAction)]
            if sub:
                theme_parser = sub[0].choices.get("theme")
                if theme_parser:
                    theme_parser.print_help()
            sys.exit(0)
        args.func(args)
    else:
        parser.print_help()

    sys.exit(0)


if __name__ == "__main__":
    main()
