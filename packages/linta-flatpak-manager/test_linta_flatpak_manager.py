#!/usr/bin/env python3
"""Unit tests for linta-flatpak-manager (PyQt6 Flatpak GUI). Tests run without display by mocking Qt."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock PyQt6 so module can be imported without a display
for mod in ("PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets"):
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import linta_flatpak_manager


class TestParseFlatpakColumns(unittest.TestCase):
    """Tests for parse_flatpak_columns()."""

    def test_parse_valid_output(self) -> None:
        output = "name\tapplication\tversion\ndesktop\torg.gnome.Calculator\t1.0"
        rows = linta_flatpak_manager.parse_flatpak_columns(output)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], ["desktop", "org.gnome.Calculator", "1.0"])

    def test_parse_skips_header(self) -> None:
        output = "col1\tcol2\na\tb\nc\td"
        rows = linta_flatpak_manager.parse_flatpak_columns(output)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], ["a", "b"])
        self.assertEqual(rows[1], ["c", "d"])

    def test_parse_empty_returns_empty_list(self) -> None:
        self.assertEqual(linta_flatpak_manager.parse_flatpak_columns(""), [])
        self.assertEqual(linta_flatpak_manager.parse_flatpak_columns("\n\n"), [])

    def test_parse_header_only_returns_empty_list(self) -> None:
        output = "name\tapplication\n"
        rows = linta_flatpak_manager.parse_flatpak_columns(output)
        self.assertEqual(rows, [])


class TestAppInfo(unittest.TestCase):
    """Tests for AppInfo dataclass."""

    def test_app_info_creation(self) -> None:
        app = linta_flatpak_manager.AppInfo(
            name="Calculator",
            app_id="org.gnome.Calculator",
            version="1.0",
            description="A calculator",
            installed=True,
        )
        self.assertEqual(app.name, "Calculator")
        self.assertEqual(app.app_id, "org.gnome.Calculator")
        self.assertEqual(app.version, "1.0")
        self.assertEqual(app.description, "A calculator")
        self.assertTrue(app.installed)

    def test_app_info_defaults(self) -> None:
        app = linta_flatpak_manager.AppInfo(name="App", app_id="org.example.App")
        self.assertEqual(app.version, "")
        self.assertEqual(app.description, "")
        self.assertFalse(app.installed)


class TestRunFlatpakSync(unittest.TestCase):
    """Tests for run_flatpak_sync() with mocked subprocess."""

    @patch("linta_flatpak_manager.subprocess.run")
    def test_run_flatpak_sync_success(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
        ok, out = linta_flatpak_manager.run_flatpak_sync(["list"])
        self.assertTrue(ok)
        self.assertIn("ok", out)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[:2], ["flatpak", "list"])

    @patch("linta_flatpak_manager.subprocess.run")
    def test_run_flatpak_sync_failure(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        ok, out = linta_flatpak_manager.run_flatpak_sync(["install", "bad"])
        self.assertFalse(ok)
        self.assertIn("error", out)


class TestFilterApp(unittest.TestCase):
    """Tests for _filter_app logic (search filter). Logic: q in name/description/app_id."""

    @staticmethod
    def _filter_app(app: linta_flatpak_manager.AppInfo, search_filter: str) -> bool:
        """Replicate LintaFlatpakManager._filter_app for testing without GUI."""
        if not search_filter:
            return True
        q = search_filter.strip().lower()
        return (
            q in app.name.lower()
            or q in (app.description or "").lower()
            or q in app.app_id.lower()
        )

    def test_filter_app_empty_filter_matches_all(self) -> None:
        app = linta_flatpak_manager.AppInfo("Test", "org.test.App", description="Desc")
        self.assertTrue(self._filter_app(app, ""))

    def test_filter_app_matches_name(self) -> None:
        app = linta_flatpak_manager.AppInfo("Calculator", "org.gnome.Calculator")
        self.assertTrue(self._filter_app(app, "calc"))

    def test_filter_app_matches_app_id(self) -> None:
        app = linta_flatpak_manager.AppInfo("Calc", "org.gnome.Calculator")
        self.assertTrue(self._filter_app(app, "gnome"))

    def test_filter_app_no_match_returns_false(self) -> None:
        app = linta_flatpak_manager.AppInfo("Calculator", "org.gnome.Calculator")
        self.assertFalse(self._filter_app(app, "nonexistent"))


class TestModuleConstants(unittest.TestCase):
    """Smoke test: module imports and exposes expected names."""

    def test_parse_flatpak_columns_exported(self) -> None:
        self.assertTrue(callable(linta_flatpak_manager.parse_flatpak_columns))

    def test_run_flatpak_sync_exported(self) -> None:
        self.assertTrue(callable(linta_flatpak_manager.run_flatpak_sync))

    def test_app_info_exported(self) -> None:
        self.assertEqual(linta_flatpak_manager.AppInfo.__name__, "AppInfo")


if __name__ == "__main__":
    unittest.main()
