#!/usr/bin/env python3
"""Unit tests for linta-welcome (PyQt6 welcome app). Tests run without display by mocking Qt."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Fake Qt base classes so we can import the module without a display.
# Using real-looking base classes prevents MagicMock from hiding class attributes.
class FakeQWidget:
    pass

class FakeQFrame(FakeQWidget):
    pass

class FakeQWizardPage(FakeQWidget):
    pass

class FakeQWizard(FakeQWidget):
    def setWindowTitle(self, title):  # noqa: N802
        pass
    def addPage(self, page):
        pass

def _install_qt_mocks() -> None:
    mock_core = MagicMock()
    mock_gui = MagicMock()
    mock_widgets = MagicMock()
    mock_widgets.QWidget = FakeQWidget
    mock_widgets.QFrame = FakeQFrame
    mock_widgets.QWizardPage = FakeQWizardPage
    mock_widgets.QWizard = FakeQWizard
    # Stub other used symbols so imports succeed
    for name in (
        "QApplication", "QVBoxLayout", "QHBoxLayout", "QLabel", "QPushButton",
        "QRadioButton", "QButtonGroup", "QGroupBox", "QCheckBox", "QComboBox",
        "QLineEdit", "QScrollArea", "QGridLayout", "QSizePolicy", "QMessageBox",
        "QSize", "Qt", "QFont", "QColor", "QPalette", "QIcon",
    ):
        if not hasattr(mock_widgets, name):
            setattr(mock_widgets, name, MagicMock())
        if name in ("QSize", "Qt") and hasattr(mock_core, name):
            continue
        if not hasattr(mock_core, name):
            setattr(mock_core, name, MagicMock())
        if not hasattr(mock_gui, name):
            setattr(mock_gui, name, MagicMock())
    sys.modules["PyQt6"] = MagicMock()
    sys.modules["PyQt6.QtCore"] = mock_core
    sys.modules["PyQt6.QtGui"] = mock_gui
    sys.modules["PyQt6.QtWidgets"] = mock_widgets

_install_qt_mocks()
import linta_welcome


class TestGetProfile(unittest.TestCase):
    """Tests for _get_profile()."""

    def test_get_profile_reads_variant_id(self) -> None:
        content = 'VARIANT_ID="kde"\n'
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / "linta-release"
            release.write_text(content)
            with patch("linta_welcome.RELEASE_FILE", release):
                self.assertEqual(linta_welcome._get_profile(), "kde")

    def test_get_profile_niri(self) -> None:
        content = "VARIANT_ID=niri\n"
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / "linta-release"
            release.write_text(content)
            with patch("linta_welcome.RELEASE_FILE", release):
                self.assertEqual(linta_welcome._get_profile(), "niri")

    def test_get_profile_falls_back_to_kde_when_no_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / "nonexistent"
            with patch("linta_welcome.RELEASE_FILE", release):
                self.assertEqual(linta_welcome._get_profile(), "kde")


class TestRun(unittest.TestCase):
    """Tests for _run()."""

    def test_run_simple_command(self) -> None:
        result = linta_welcome._run(["true"])
        self.assertEqual(result.returncode, 0)

    def test_run_capture_output(self) -> None:
        result = linta_welcome._run(["echo", "hello"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("hello", result.stdout)


class TestFileManagerOptions(unittest.TestCase):
    """Tests for FileManagerPage._get_options() (pure logic, no GUI)."""

    def test_get_options_kde_default(self) -> None:
        opts = linta_welcome.FileManagerPage._get_options("kde")
        names = [o["name"] for o in opts]
        self.assertIn("Dolphin", names)
        dolphin = next(o for o in opts if o["name"] == "Dolphin")
        self.assertTrue(dolphin.get("default"))

    def test_get_options_niri_default(self) -> None:
        opts = linta_welcome.FileManagerPage._get_options("niri")
        spacefm = next((o for o in opts if o["name"] == "SpaceFM"), None)
        self.assertIsNotNone(spacefm)
        self.assertTrue(spacefm.get("default"))

    def test_get_options_has_package_and_description(self) -> None:
        opts = linta_welcome.FileManagerPage._get_options("combined")
        for o in opts:
            self.assertIn("name", o)
            self.assertIn("package", o)
            self.assertIn("description", o)


class TestThemePickerOptions(unittest.TestCase):
    """Tests for ThemePickerPage._get_options() (pure logic)."""

    def test_get_options_kde_only_lists_supported_choices(self) -> None:
        opts = linta_welcome.ThemePickerPage._get_options("kde")
        names = [o["name"] for o in opts]
        self.assertIn("Linta (KDE)", names)
        self.assertNotIn("Breeze", names)

    def test_get_options_niri_has_supported_rices_only(self) -> None:
        opts = linta_welcome.ThemePickerPage._get_options("niri")
        names = [o["name"] for o in opts]
        self.assertIn("Dusk", names)
        self.assertIn("Frost", names)
        self.assertNotIn("Vanilla Niri", names)

    def test_get_options_combined_has_both(self) -> None:
        opts = linta_welcome.ThemePickerPage._get_options("combined")
        names = [o["name"] for o in opts]
        self.assertIn("Linta (KDE)", names)
        self.assertIn("Dusk", names)


class TestFontWizardPresets(unittest.TestCase):
    """Tests for FontWizardPage.PRESETS structure."""

    def test_presets_have_required_keys(self) -> None:
        for name, info in linta_welcome.FontWizardPage.PRESETS.items():
            self.assertIn("packages", info, msg=name)
            self.assertIn("description", info, msg=name)
            self.assertIsInstance(info["packages"], list, msg=name)
            self.assertGreater(len(info["packages"]), 0, msg=name)

    def test_bare_minimum_preset_exists(self) -> None:
        self.assertIn("Bare Minimum", linta_welcome.FontWizardPage.PRESETS)


class TestTerminalPageData(unittest.TestCase):
    """Tests for TerminalPage.TERMINALS structure."""

    def test_terminals_have_name_package_description(self) -> None:
        for t in linta_welcome.TerminalPage.TERMINALS:
            self.assertIn("name", t)
            self.assertIn("package", t)
            self.assertIn("description", t)

    def test_wezterm_is_option(self) -> None:
        names = [t["name"] for t in linta_welcome.TerminalPage.TERMINALS]
        self.assertIn("WezTerm", names)


class TestThemeMap(unittest.TestCase):
    """Tests for theme name to theme_id mapping used in _apply_theme."""

    def test_theme_map_covers_niri_rices_and_kde(self) -> None:
        self.assertEqual(linta_welcome._theme_id_for_name("Linta (KDE)"), "linta-kde-default")
        self.assertEqual(linta_welcome._theme_id_for_name("Dusk"), "linta-niri-rice-1")
        self.assertEqual(linta_welcome._theme_id_for_name("Frost"), "linta-niri-rice-2")
        self.assertEqual(linta_welcome._theme_id_for_name("Unknown"), "")


class TestLocaleApplication(unittest.TestCase):
    """Tests for timezone/locale application helpers."""

    @patch("linta_welcome._run")
    def test_apply_locale_settings_uses_privileged_system_tools(self, mock_run) -> None:
        mock_run.return_value = MagicMock(returncode=0)

        result = linta_welcome._apply_locale_settings("pl_PL.UTF-8", "Europe/Warsaw")

        self.assertTrue(result)
        self.assertEqual(
            mock_run.call_args_list[0].args[0],
            ["pkexec", "localectl", "set-locale", "LANG=pl_PL.UTF-8"],
        )
        self.assertEqual(
            mock_run.call_args_list[1].args[0],
            ["pkexec", "timedatectl", "set-timezone", "Europe/Warsaw"],
        )


class TestModuleConstants(unittest.TestCase):
    """Smoke test: module imports and exposes expected constants."""

    def test_version_defined(self) -> None:
        self.assertTrue(hasattr(linta_welcome, "VERSION"))
        self.assertIsInstance(linta_welcome.VERSION, str)

    def test_release_file_path(self) -> None:
        self.assertEqual(linta_welcome.RELEASE_FILE, Path("/etc/linta-release"))


class TestAcceptMarkerWrite(unittest.TestCase):
    """Test that marker write failure does not crash."""

    def test_accept_does_not_crash_when_marker_write_is_denied(self) -> None:
        """When _write_first_boot_marker raises OSError internally, it does not propagate."""
        marker = MagicMock()
        marker.parent.mkdir.return_value = None
        marker.write_text.side_effect = OSError("Permission denied")
        with patch("linta_welcome.FIRST_BOOT_MARKER", marker):
            linta_welcome._write_first_boot_marker()
        marker.write_text.assert_called_once_with("done\n")


if __name__ == "__main__":
    unittest.main()
