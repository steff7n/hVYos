"""DNF plugin for automatic pre-transaction Btrfs snapshots.

Creates a snapshot before every package install, update, or remove.
Spec reference: README.md §2.1, §3.2

Profiles: [All]
"""

from __future__ import annotations

import subprocess
from datetime import datetime

import dnf  # type: ignore[import-untyped]
import dnf.cli  # type: ignore[import-untyped]


class LintaSnapshotPlugin(dnf.Plugin):
    name = "linta-snapshot"

    def __init__(self, base: dnf.Base, cli: dnf.cli.Cli | None) -> None:
        super().__init__(base, cli)

    def pre_transaction(self) -> None:
        """Create a Btrfs snapshot before every DNF transaction."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        actions = []
        for tsi in self.base.transaction:
            if tsi.action in (
                dnf.transaction.PKG_INSTALL,
                dnf.transaction.PKG_UPGRADE,
                dnf.transaction.PKG_ERASE,
            ):
                actions.append(f"{tsi.action_short} {tsi.pkg}")

        if not actions:
            return

        action_summary = ", ".join(actions[:5])
        if len(actions) > 5:
            action_summary += f" (+{len(actions) - 5} more)"

        description = f"dnf-{timestamp}: {action_summary}"

        try:
            subprocess.run(
                [
                    "snapper", "-c", "root", "create",
                    "--type", "single",
                    "--description", description,
                    "--cleanup-algorithm", "number",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # non-fatal: don't block package operations

    def transaction(self) -> None:
        """After transaction: update GRUB snapshot entries."""
        try:
            subprocess.run(
                ["linta-snapshots", "grub-update"],
                check=False,
                capture_output=True,
            )
        except FileNotFoundError:
            pass
