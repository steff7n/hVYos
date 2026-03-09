#!/usr/bin/env python3
"""Unit tests for lintactl CLI tool."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import lintactl


class TestReadRelease(unittest.TestCase):
    """Tests for _read_release()."""

    def test_read_release_valid_data(self) -> None:
        """Parse valid key=value format from release file."""
        content = 'VERSION="1.0"\nVARIANT_ID=kde\nNAME="Linta Linux"\n'
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(content)
            with patch("lintactl.RELEASE_FILE", release_file):
                result = lintactl._read_release()
        self.assertEqual(result["VERSION"], "1.0")
        self.assertEqual(result["VARIANT_ID"], "kde")
        self.assertEqual(result["NAME"], "Linta Linux")

    def test_read_release_missing_file(self) -> None:
        """Return empty dict when release file does not exist."""
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "nonexistent"
            with patch("lintactl.RELEASE_FILE", release_file):
                result = lintactl._read_release()
        self.assertEqual(result, {})

    def test_read_release_comments_and_empty_lines(self) -> None:
        """Skip comments and empty lines, strip quotes from values."""
        content = """
# This is a comment
VARIANT_ID=niri

NAME="Linta"
# Another comment
VERSION=2.0
"""
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(content)
            with patch("lintactl.RELEASE_FILE", release_file):
                result = lintactl._read_release()
        self.assertEqual(result["VARIANT_ID"], "niri")
        self.assertEqual(result["NAME"], "Linta")
        self.assertEqual(result["VERSION"], "2.0")
        self.assertNotIn("#", "".join(result.keys()))


class TestGetProfile(unittest.TestCase):
    """Tests for _get_profile()."""

    def test_get_profile_returns_variant_from_release(self) -> None:
        """Return VARIANT_ID from release file."""
        content = "VARIANT_ID=combined\n"
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(content)
            with patch("lintactl.RELEASE_FILE", release_file):
                result = lintactl._get_profile()
        self.assertEqual(result, "combined")

    def test_get_profile_returns_unknown_when_no_file(self) -> None:
        """Return 'unknown' when release file does not exist."""
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "nonexistent"
            with patch("lintactl.RELEASE_FILE", release_file):
                result = lintactl._get_profile()
        self.assertEqual(result, "unknown")


class TestGetActiveTheme(unittest.TestCase):
    """Tests for _get_active_theme()."""

    def test_get_active_theme_reads_from_file(self) -> None:
        """Read active theme from ACTIVE_THEME_FILE when it exists."""
        with tempfile.TemporaryDirectory() as tmp:
            theme_file = Path(tmp) / "active-theme"
            theme_file.write_text("my-custom-theme\n")
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=kde\n")
            with patch("lintactl.ACTIVE_THEME_FILE", theme_file), patch(
                "lintactl.RELEASE_FILE", release_file
            ):
                result = lintactl._get_active_theme()
        self.assertEqual(result, "my-custom-theme")

    def test_get_active_theme_falls_back_to_profile_default(self) -> None:
        """Fall back to profile-based default when theme file missing."""
        with tempfile.TemporaryDirectory() as tmp:
            theme_file = Path(tmp) / "nonexistent"
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=kde\n")
            with patch("lintactl.ACTIVE_THEME_FILE", theme_file), patch(
                "lintactl.RELEASE_FILE", release_file
            ):
                result = lintactl._get_active_theme()
        self.assertEqual(result, "linta-kde-default")

    def test_get_active_theme_niri_profile_default(self) -> None:
        """niri profile defaults to linta-niri-rice1."""
        with tempfile.TemporaryDirectory() as tmp:
            theme_file = Path(tmp) / "nonexistent"
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=niri\n")
            with patch("lintactl.ACTIVE_THEME_FILE", theme_file), patch(
                "lintactl.RELEASE_FILE", release_file
            ):
                result = lintactl._get_active_theme()
        self.assertEqual(result, "linta-niri-rice1")

    def test_get_active_theme_unknown_profile_returns_none(self) -> None:
        """Unknown profile returns 'none'."""
        with tempfile.TemporaryDirectory() as tmp:
            theme_file = Path(tmp) / "nonexistent"
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=bare\n")
            with patch("lintactl.ACTIVE_THEME_FILE", theme_file), patch(
                "lintactl.RELEASE_FILE", release_file
            ):
                result = lintactl._get_active_theme()
        self.assertEqual(result, "none")


class TestBuildParser(unittest.TestCase):
    """Tests for build_parser()."""

    def test_build_parser_creates_parser_with_all_subcommands(self) -> None:
        """Parser has info, profile, theme, nvidia, font-wizard, snapshot."""
        parser = lintactl.build_parser()
        self.assertIsNotNone(parser)

        # Get subparser choices
        subparser_action = None
        for action in parser._actions:
            if hasattr(action, "choices") and action.choices:
                subparser_action = action
                break
        self.assertIsNotNone(subparser_action)
        choices = subparser_action.choices

        self.assertIn("info", choices)
        self.assertIn("profile", choices)
        self.assertIn("theme", choices)
        self.assertIn("nvidia", choices)
        self.assertIn("font-wizard", choices)
        self.assertIn("snapshot", choices)

        # Theme has list and set subcommands
        theme_parser = choices["theme"]
        theme_sub = [
            a for a in theme_parser._actions
            if hasattr(a, "choices") and a.choices
        ]
        self.assertGreater(len(theme_sub), 0)
        theme_choices = theme_sub[0].choices
        self.assertIn("list", theme_choices)
        self.assertIn("set", theme_choices)


class TestCmdInfo(unittest.TestCase):
    """Tests for cmd_info()."""

    def test_cmd_info_outputs_system_info(self) -> None:
        """cmd_info prints system info with mocked subprocess calls."""
        release_content = "VERSION=1.0\nVARIANT_ID=kde\nNAME=Linta\n"
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(release_content)
            theme_file = Path(tmp) / "active-theme"
            theme_file.write_text("linta-kde-default\n")

            mock_run = MagicMock()
            mock_run.return_value.stdout = "6.6.126\n"
            mock_run.side_effect = [
                MagicMock(stdout="6.6.126\n"),
                MagicMock(stdout="btrfs\n"),
                MagicMock(stdout="Enforcing\n"),
            ]

            args = MagicMock(json=False)
            with patch("lintactl.RELEASE_FILE", release_file), patch(
                "lintactl.ACTIVE_THEME_FILE", theme_file
            ), patch("lintactl.subprocess.run", mock_run):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_info(args)

            output = capture.getvalue()
            self.assertIn("Linta 1.0", output)
            self.assertIn("Profile:    kde", output)
            self.assertIn("Theme:      linta-kde-default", output)
            self.assertIn("Kernel:     6.6.126", output)
            self.assertIn("Btrfs (active)", output)
            self.assertIn("SELinux:    Enforcing", output)

    def test_cmd_info_json_output(self) -> None:
        """cmd_info --json outputs valid JSON."""
        release_content = "VERSION=1.0\nVARIANT_ID=kde\nNAME=Linta\n"
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(release_content)
            theme_file = Path(tmp) / "active-theme"
            theme_file.write_text("linta-kde-default\n")

            mock_run = MagicMock()
            mock_run.side_effect = [
                MagicMock(stdout="6.6.126\n"),
                MagicMock(stdout="btrfs\n"),
                MagicMock(stdout="Enforcing\n"),
            ]

            args = MagicMock(json=True)
            with patch("lintactl.RELEASE_FILE", release_file), patch(
                "lintactl.ACTIVE_THEME_FILE", theme_file
            ), patch("lintactl.subprocess.run", mock_run):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_info(args)

            output = capture.getvalue()
            # JSON is printed after the human-readable lines; find it
            json_start = output.find("{")
            self.assertGreater(json_start, 0, "JSON output not found")
            data = json.loads(output[json_start:])
            self.assertEqual(data["profile"], "kde")
            self.assertEqual(data["theme"], "linta-kde-default")
            self.assertEqual(data["kernel"], "6.6.126")
            self.assertEqual(data["btrfs"], "active")
            self.assertEqual(data["selinux"], "Enforcing")

    def test_cmd_info_non_btrfs_prints_actual_filesystem(self) -> None:
        """Non-Btrfs roots should not be labeled as Btrfs."""
        release_content = "VERSION=1.0\nVARIANT_ID=kde\nNAME=Linta\n"
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text(release_content)
            theme_file = Path(tmp) / "active-theme"
            theme_file.write_text("linta-kde-default\n")

            mock_run = MagicMock()
            mock_run.side_effect = [
                MagicMock(stdout="6.6.126\n"),
                MagicMock(stdout="ext4\n"),
                MagicMock(stdout="Enforcing\n"),
            ]

            args = MagicMock(json=False)
            with patch("lintactl.RELEASE_FILE", release_file), patch(
                "lintactl.ACTIVE_THEME_FILE", theme_file
            ), patch("lintactl.subprocess.run", mock_run):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_info(args)

            output = capture.getvalue()
            self.assertIn("Filesystem: ext4", output)
            self.assertNotIn("Filesystem: Btrfs (ext4)", output)


class TestCmdProfile(unittest.TestCase):
    """Tests for cmd_profile()."""

    def test_cmd_profile_outputs_profile_name(self) -> None:
        """cmd_profile prints profile info."""
        with tempfile.TemporaryDirectory() as tmp:
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=niri\n")
            with patch("lintactl.RELEASE_FILE", release_file):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_profile(MagicMock())
            output = capture.getvalue()
            self.assertIn("Profile: niri", output)
            self.assertIn("Niri", output)


class TestCmdThemeList(unittest.TestCase):
    """Tests for cmd_theme_list()."""

    def test_cmd_theme_list_with_themes_directory(self) -> None:
        """List themes from THEMES_DIR with metadata."""
        with tempfile.TemporaryDirectory() as tmp:
            themes_dir = Path(tmp) / "themes"
            themes_dir.mkdir()
            (themes_dir / "theme-a").mkdir()
            (themes_dir / "theme-b").mkdir()
            (themes_dir / "theme-a" / "metadata.json").write_text(
                '{"description": "Theme A", "profile": "kde"}'
            )

            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=kde\n")
            theme_file = Path(tmp) / "active-theme"
            theme_file.write_text("theme-a\n")

            with patch("lintactl.THEMES_DIR", themes_dir), patch(
                "lintactl.RELEASE_FILE", release_file
            ), patch("lintactl.ACTIVE_THEME_FILE", theme_file):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_theme_list(MagicMock())

            output = capture.getvalue()
            self.assertIn("theme-a", output)
            self.assertIn("theme-b", output)
            self.assertIn(" *", output)  # Active marker
            self.assertIn("Theme A", output)

    def test_cmd_theme_list_missing_themes_dir(self) -> None:
        """Show message when themes directory does not exist."""
        with tempfile.TemporaryDirectory() as tmp:
            themes_dir = Path(tmp) / "nonexistent"
            release_file = Path(tmp) / "linta-release"
            release_file.write_text("VARIANT_ID=kde\n")
            with patch("lintactl.THEMES_DIR", themes_dir), patch(
                "lintactl.RELEASE_FILE", release_file
            ):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_theme_list(MagicMock())
            output = capture.getvalue()
            self.assertIn("No themes installed", output)


class TestCmdThemeSet(unittest.TestCase):
    """Tests for cmd_theme_set()."""

    def test_cmd_theme_set_nonexistent_theme_exits_with_error(self) -> None:
        """Exit with error when theme does not exist."""
        with tempfile.TemporaryDirectory() as tmp:
            themes_dir = Path(tmp) / "themes"
            themes_dir.mkdir()
            # No "missing-theme" subdir

            args = MagicMock()
            args.name = "missing-theme"
            with patch("lintactl.THEMES_DIR", themes_dir):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    with self.assertRaises(SystemExit) as cm:
                        lintactl.cmd_theme_set(args)
                self.assertEqual(cm.exception.code, 1)
            output = capture.getvalue()
            self.assertIn("Error", output)
            self.assertIn("missing-theme", output)
            self.assertIn("not found", output)

    def test_cmd_theme_set_theme_without_apply_sh_exits_with_error(
        self,
    ) -> None:
        """Exit with error when theme has no apply.sh script."""
        with tempfile.TemporaryDirectory() as tmp:
            themes_dir = Path(tmp) / "themes"
            themes_dir.mkdir()
            (themes_dir / "no-script-theme").mkdir()
            # No apply.sh

            args = MagicMock()
            args.name = "no-script-theme"
            with patch("lintactl.THEMES_DIR", themes_dir):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    with self.assertRaises(SystemExit) as cm:
                        lintactl.cmd_theme_set(args)
                self.assertEqual(cm.exception.code, 1)
            output = capture.getvalue()
            self.assertIn("no apply.sh", output)

    def test_cmd_theme_set_success(self) -> None:
        """Successfully set theme and write active-theme file."""
        with tempfile.TemporaryDirectory() as tmp:
            themes_dir = Path(tmp) / "themes"
            themes_dir.mkdir()
            theme_dir = themes_dir / "good-theme"
            theme_dir.mkdir()
            apply_script = theme_dir / "apply.sh"
            apply_script.write_text("#!/bin/bash\necho 'applied'\n")

            active_theme_dir = Path(tmp) / "linta" / "etc"
            active_theme_file = active_theme_dir / "active-theme"

            args = MagicMock()
            args.name = "good-theme"
            mock_run = MagicMock(
                return_value=MagicMock(stdout="applied\n", returncode=0)
            )

            with patch("lintactl.THEMES_DIR", themes_dir), patch(
                "lintactl.ACTIVE_THEME_FILE", active_theme_file
            ), patch("lintactl.subprocess.run", mock_run):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    lintactl.cmd_theme_set(args)

            output = capture.getvalue()
            self.assertIn("Applying theme 'good-theme'", output)
            self.assertIn("Theme set to 'good-theme'", output)
            self.assertTrue(active_theme_file.exists())
            self.assertEqual(
                active_theme_file.read_text().strip(), "good-theme"
            )
            mock_run.assert_called_once()

    def test_cmd_theme_set_rejects_path_traversal(self) -> None:
        """Theme names must not escape the configured themes directory."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            themes_dir = root / "themes"
            themes_dir.mkdir()
            evil_theme = root / "evil"
            evil_theme.mkdir()
            (evil_theme / "apply.sh").write_text("#!/bin/bash\necho 'evil'\n")
            active_theme_file = root / "etc" / "active-theme"

            args = MagicMock()
            args.name = "../evil"

            mock_run = MagicMock(return_value=MagicMock(stdout="evil\n", returncode=0))
            with patch("lintactl.THEMES_DIR", themes_dir), patch(
                "lintactl.ACTIVE_THEME_FILE", active_theme_file
            ), patch("lintactl.subprocess.run", mock_run):
                capture = StringIO()
                with patch("sys.stdout", capture):
                    with self.assertRaises(SystemExit) as cm:
                        lintactl.cmd_theme_set(args)
                self.assertEqual(cm.exception.code, 1)
            output = capture.getvalue()
            self.assertIn("invalid theme name", output)
            self.assertFalse(active_theme_file.exists())
            mock_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
