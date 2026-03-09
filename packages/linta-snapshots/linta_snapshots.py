#!/usr/bin/env python3
"""linta-snapshots — Btrfs snapshot management for Linta Linux.

Wraps snapper with Linta-specific workflows:
- Pre-transaction snapshots (DNF plugin)
- Weekly scheduled snapshots (via systemd timer)
- GRUB menu integration (last 5 snapshots)
- CLI for browsing and managing snapshots

Profiles: [All]
Spec reference: README.md §3.2, §6.1
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn

VERSION = "0.1.0"
GRUB_SNAPSHOT_CFG = Path("/etc/grub.d/45_linta_snapshots")
GRUB_CFG = Path("/boot/grub2/grub.cfg")
SNAPPER_CONFIG = "root"
MAX_GRUB_SNAPSHOTS = 5


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _require_root() -> None:
    if os.geteuid() != 0:
        print("  Error: this command requires root privileges.")
        print("  Run with: sudo linta-snapshots ...")
        sys.exit(1)


def _parse_snapper_list() -> list[dict[str, str]]:
    """Parse `snapper list --columns` output into structured data."""
    try:
        result = _run(["snapper", "-c", SNAPPER_CONFIG, "list", "--columns",
                        "number,type,date,description,cleanup"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    snapshots = []
    lines = result.stdout.strip().splitlines()
    for line in lines[2:]:  # skip header + separator
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4 and parts[0].isdigit():
            snapshots.append({
                "number": parts[0],
                "type": parts[1] if len(parts) > 1 else "",
                "date": parts[2] if len(parts) > 2 else "",
                "description": parts[3] if len(parts) > 3 else "",
                "cleanup": parts[4] if len(parts) > 4 else "",
            })
    return snapshots


def _get_root_uuid() -> str:
    try:
        result = _run(["findmnt", "-n", "-o", "UUID", "/"])
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _get_boot_artifact_names(boot_dir: Path = Path("/boot")) -> tuple[str, str]:
    """Return the current kernel and initramfs filenames."""
    kernels = sorted(path.name for path in boot_dir.glob("vmlinuz-*") if path.is_file())
    initramfs = sorted(path.name for path in boot_dir.glob("initramfs-*.img") if path.is_file())

    if not kernels or not initramfs:
        raise RuntimeError("could not determine kernel/initramfs names for GRUB snapshots")

    return kernels[-1], initramfs[-1]


def cmd_list(args: argparse.Namespace) -> None:
    """List all Btrfs snapshots."""
    snapshots = _parse_snapper_list()

    if not snapshots:
        print("  No snapshots found.")
        return

    if args.json:
        print(json.dumps(snapshots, indent=2))
        return

    print(f"  {'#':<6} {'Type':<10} {'Date':<22} {'Description'}")
    print(f"  {'─'*6} {'─'*10} {'─'*22} {'─'*30}")
    for s in snapshots:
        print(f"  {s['number']:<6} {s['type']:<10} {s['date']:<22} {s['description']}")

    print(f"\n  Total: {len(snapshots)} snapshot(s)")
    grub_count = min(len(snapshots), MAX_GRUB_SNAPSHOTS)
    print(f"  GRUB menu shows last {grub_count}")


def cmd_create(args: argparse.Namespace) -> None:
    """Create a new snapshot."""
    _require_root()

    desc = args.description or f"manual-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    cleanup = "number"

    print(f"  Creating snapshot: {desc}")
    try:
        result = _run([
            "snapper", "-c", SNAPPER_CONFIG, "create",
            "--type", "single",
            "--description", desc,
            "--cleanup-algorithm", cleanup,
        ])
        print(f"  Snapshot created.")
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr}")
        sys.exit(1)

    if not args.no_grub:
        try:
            _update_grub_entries()
        except RuntimeError as e:
            print(f"  Error: {e}")
            sys.exit(1)


def cmd_rollback(args: argparse.Namespace) -> None:
    """Rollback to a specific snapshot."""
    _require_root()

    snapshot_num = args.number
    print(f"  Rolling back to snapshot #{snapshot_num}...")
    print(f"  WARNING: This will make snapshot #{snapshot_num} the active system.")
    print(f"  A snapshot of the current state will be created first.")

    if not args.yes:
        confirm = input("  Continue? [y/N] ").strip().lower()
        if confirm not in ("y", "yes"):
            print("  Aborted.")
            sys.exit(0)

    try:
        _run(["snapper", "-c", SNAPPER_CONFIG, "create",
              "--type", "single",
              "--description", f"pre-rollback-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
              "--cleanup-algorithm", "number"])

        _run(["snapper", "-c", SNAPPER_CONFIG, "rollback", snapshot_num])
        print(f"  Rollback complete. Reboot to activate snapshot #{snapshot_num}.")
        print(f"  Run: sudo systemctl reboot")
    except subprocess.CalledProcessError as e:
        print(f"  Error during rollback: {e.stderr}")
        sys.exit(1)


def cmd_grub_update(args: argparse.Namespace) -> None:
    """Update GRUB menu with the last N snapshots."""
    _require_root()
    try:
        _update_grub_entries()
    except RuntimeError as e:
        print(f"  Error: {e}")
        sys.exit(1)
    print("  GRUB menu updated.")


def _update_grub_entries() -> None:
    """Generate GRUB menu entries for the last N snapshots."""
    snapshots = _parse_snapper_list()
    recent = snapshots[-MAX_GRUB_SNAPSHOTS:] if len(snapshots) > MAX_GRUB_SNAPSHOTS else snapshots

    if not recent:
        return

    root_uuid = _get_root_uuid()
    if not root_uuid:
        raise RuntimeError("could not determine root filesystem UUID for GRUB snapshots")
    kernel_name, initramfs_name = _get_boot_artifact_names()

    script_lines = [
        "#!/bin/bash",
        "# Auto-generated by linta-snapshots — do not edit manually",
        'cat <<\'GRUB_EOF\'',
        'submenu "Linta Snapshots" {',
    ]

    for snap in reversed(recent):
        num = snap["number"]
        desc = snap["description"] or f"snapshot-{num}"
        date = snap["date"]
        script_lines.extend([
            f'  menuentry "Snapshot #{num}: {desc} ({date})" {{',
            f'    insmod btrfs',
            f'    search --no-floppy --fs-uuid --set=root {root_uuid}',
            f'    linux /@/.snapshots/{num}/snapshot/boot/{kernel_name} root=UUID={root_uuid} '
            f'rootflags=subvol=@/.snapshots/{num}/snapshot ro rhgb quiet',
            f'    initrd /@/.snapshots/{num}/snapshot/boot/{initramfs_name}',
            f'  }}',
        ])

    script_lines.extend([
        '}',
        'GRUB_EOF',
    ])

    GRUB_SNAPSHOT_CFG.write_text("\n".join(script_lines) + "\n")
    GRUB_SNAPSHOT_CFG.chmod(0o755)

    try:
        _run(["grub2-mkconfig", "-o", str(GRUB_CFG)])
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass


def cmd_diff(args: argparse.Namespace) -> None:
    """Show changes between current system and a snapshot."""
    snapshot_num = args.number

    try:
        result = _run([
            "snapper", "-c", SNAPPER_CONFIG, "status",
            f"{snapshot_num}..0"
        ])
        if result.stdout.strip():
            print(result.stdout)
        else:
            print(f"  No differences from snapshot #{snapshot_num}.")
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e.stderr}")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linta-snapshots",
        description="Btrfs snapshot management for Linta Linux",
    )
    parser.add_argument("--version", action="version", version=f"linta-snapshots {VERSION}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # list
    p_list = sub.add_parser("list", help="List all snapshots")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    # create
    p_create = sub.add_parser("create", help="Create a new snapshot")
    p_create.add_argument("-d", "--description", help="Snapshot description")
    p_create.add_argument("--no-grub", action="store_true",
                          help="Don't update GRUB menu after creating")
    p_create.set_defaults(func=cmd_create)

    # rollback
    p_rollback = sub.add_parser("rollback", help="Rollback to a snapshot")
    p_rollback.add_argument("number", help="Snapshot number to rollback to")
    p_rollback.add_argument("-y", "--yes", action="store_true",
                            help="Skip confirmation prompt")
    p_rollback.set_defaults(func=cmd_rollback)

    # grub-update
    p_grub = sub.add_parser("grub-update", help="Update GRUB snapshot menu entries")
    p_grub.set_defaults(func=cmd_grub_update)

    # diff
    p_diff = sub.add_parser("diff", help="Show changes since a snapshot")
    p_diff.add_argument("number", help="Snapshot number to compare against")
    p_diff.set_defaults(func=cmd_diff)

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
