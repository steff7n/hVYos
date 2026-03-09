#!/usr/bin/env python3
"""Unit tests for the Linta installer."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import linta_installer


class TestPartitionDevice(unittest.TestCase):
    """Tests for partition device path derivation."""

    def test_partition_device_handles_nvme_and_sata_names(self) -> None:
        self.assertEqual(
            linta_installer._partition_device("/dev/nvme0n1", 1),
            "/dev/nvme0n1p1",
        )
        self.assertEqual(
            linta_installer._partition_device("/dev/nvme0n1", 3),
            "/dev/nvme0n1p3",
        )
        self.assertEqual(
            linta_installer._partition_device("/dev/sda", 2),
            "/dev/sda2",
        )


class TestMainFlow(unittest.TestCase):
    """Tests for installer control flow."""

    def test_main_restarts_flow_when_confirmation_returns_back(self) -> None:
        stdscr = MagicMock()

        with (
            patch("linta_installer.curses.curs_set"),
            patch("linta_installer.curses.use_default_colors"),
            patch("linta_installer.curses.init_pair"),
            patch("linta_installer.curses.color_pair", return_value=1),
            patch("linta_installer.screen_welcome", return_value=True),
            patch("linta_installer.screen_profile", side_effect=["kde", "niri"]) as mock_profile,
            patch("linta_installer.screen_hostname", side_effect=["alpha", "beta"]),
            patch("linta_installer.screen_locale", side_effect=["en_US.UTF-8", "en_US.UTF-8"]),
            patch("linta_installer.screen_timezone", side_effect=["UTC", "UTC"]),
            patch("linta_installer.screen_disk_encryption", side_effect=[(False, ""), (False, "")]),
            patch("linta_installer.screen_disk", side_effect=["/dev/sda", "/dev/sdb"]),
            patch("linta_installer.screen_confirmation", side_effect=[False, True]),
            patch("linta_installer.screen_progress", return_value=True) as mock_progress,
            patch("linta_installer.screen_complete"),
        ):
            result = linta_installer.main(stdscr)

        self.assertEqual(result, 0)
        self.assertEqual(mock_profile.call_count, 2)
        install_state = mock_progress.call_args.args[1]
        self.assertEqual(install_state.profile, "niri")
        self.assertEqual(install_state.disk, "/dev/sdb")


class TestInstallerHelpers(unittest.TestCase):
    """Tests for helper functions used during installation."""

    def _state(self, profile: str = "bare", luks: bool = False) -> linta_installer.InstallState:
        return linta_installer.InstallState(
            profile=profile,
            hostname="silent-pine",
            locale="pl_PL.UTF-8",
            timezone="Europe/Warsaw",
            luks=luks,
            disk="/dev/sda",
        )

    def test_package_list_varies_by_profile(self) -> None:
        bare = linta_installer._package_list_for_state(self._state("bare"))
        kde = linta_installer._package_list_for_state(self._state("kde"))
        niri = linta_installer._package_list_for_state(self._state("niri"))
        combined = linta_installer._package_list_for_state(self._state("combined", luks=True))

        self.assertNotIn("plasma-desktop", bare)
        self.assertNotIn("fuzzel", bare)
        self.assertIn("plasma-desktop", kde)
        self.assertIn("konsole", kde)
        self.assertIn("fuzzel", niri)
        self.assertIn("foot", niri)
        self.assertIn("plasma-desktop", combined)
        self.assertIn("fuzzel", combined)
        self.assertIn("cryptsetup", combined)

    def test_write_system_config_creates_locale_release_and_timezone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            linta_installer._write_system_config(root, self._state("niri"))

            self.assertEqual((root / "etc/hostname").read_text(), "silent-pine\n")
            self.assertEqual((root / "etc/locale.conf").read_text(), "LANG=pl_PL.UTF-8\n")
            self.assertEqual(
                os.readlink(root / "etc/localtime"),
                "/usr/share/zoneinfo/Europe/Warsaw",
            )
            release = (root / "etc/linta-release").read_text()
            self.assertIn("VARIANT_ID=niri", release)
            self.assertIn('ID=linta', release)

    @patch("linta_installer.subprocess.run")
    def test_create_default_user_invokes_useradd_and_chpasswd(self, mock_run) -> None:
        root = Path("/target")
        linta_installer._create_default_user(root)

        self.assertEqual(mock_run.call_count, 2)
        useradd_call = mock_run.call_args_list[0]
        chpasswd_call = mock_run.call_args_list[1]

        self.assertEqual(
            useradd_call.args[0],
            ["chroot", "/target", "useradd", "-m", "-G", "wheel", "linta"],
        )
        self.assertEqual(
            chpasswd_call.args[0],
            ["chroot", "/target", "chpasswd"],
        )
        self.assertEqual(chpasswd_call.kwargs["input"], "linta:linta\n")
        self.assertTrue(chpasswd_call.kwargs["text"])

    def test_build_dnf_install_command_uses_default_releasever(self) -> None:
        cmd = linta_installer._build_dnf_install_command(Path("/target"), ["kernel"])
        releasever_index = cmd.index("--releasever")

        self.assertEqual(linta_installer.DEFAULT_RELEASEVER, "42")
        self.assertEqual(cmd[releasever_index + 1], "42")
        self.assertEqual(cmd[:3], ["dnf", "--installroot", "/target"])


if __name__ == "__main__":
    unittest.main()
