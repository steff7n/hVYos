#!/usr/bin/env python3
"""Unit tests for linta-keybindings (runs without display)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock PyQt6 so overlay test can run without display; avoids offscreen hangs
for mod in ("PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets"):
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

import linta_keybindings


class TestKeyBinding(unittest.TestCase):
    """Tests for KeyBinding dataclass."""

    def test_key_binding_creation(self) -> None:
        b = linta_keybindings.KeyBinding(
            category="Niri",
            keys="Mod+Return",
            description="Launch terminal",
        )
        self.assertEqual(b.category, "Niri")
        self.assertEqual(b.keys, "Mod+Return")
        self.assertEqual(b.description, "Launch terminal")


class TestDetectDesktop(unittest.TestCase):
    """Tests for _detect_desktop()."""

    def test_detect_desktop_niri(self) -> None:
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "niri"}):
            self.assertEqual(linta_keybindings._detect_desktop(), "niri")

    def test_detect_desktop_kde(self) -> None:
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "KDE"}):
            self.assertEqual(linta_keybindings._detect_desktop(), "kde")

    def test_detect_desktop_plasma(self) -> None:
        with patch.dict("os.environ", {"XDG_CURRENT_DESKTOP": "plasmax11"}):
            self.assertEqual(linta_keybindings._detect_desktop(), "kde")


class TestLintaBindings(unittest.TestCase):
    """Tests for _linta_bindings()."""

    def test_linta_bindings_returns_list(self) -> None:
        bindings = linta_keybindings._linta_bindings()
        self.assertIsInstance(bindings, list)
        self.assertGreater(len(bindings), 0)

    def test_linta_bindings_contains_overlay_shortcut(self) -> None:
        bindings = linta_keybindings._linta_bindings()
        categories = [b.category for b in bindings]
        self.assertIn("Linta", categories)
        overlay = next((b for b in bindings if "keybinding" in b.description.lower()), None)
        self.assertIsNotNone(overlay)
        self.assertIn("Mod+Shift+/", overlay.keys)


class TestNiriParser(unittest.TestCase):
    """Tests for NiriParser with temp config file."""

    def test_parse_empty_file_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.kdl"
            config.write_text("")
            with patch("linta_keybindings.NIRI_CONFIG", config):
                parser = linta_keybindings.NiriParser()
                self.assertEqual(parser.parse(), [])

    def test_parse_missing_file_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "nonexistent"
            with patch("linta_keybindings.NIRI_CONFIG", config):
                parser = linta_keybindings.NiriParser()
                self.assertEqual(parser.parse(), [])

    def test_parse_extracts_binds(self) -> None:
        content = """
binds {
  Mod+Return { spawn "foot"; }
  Mod+D { spawn "niri action spawn wofi -d"; }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.kdl"
            config.write_text(content)
            with patch("linta_keybindings.NIRI_CONFIG", config):
                parser = linta_keybindings.NiriParser()
                bindings = parser.parse()
                self.assertGreater(len(bindings), 0)
                keys = [b.keys for b in bindings]
                self.assertIn("Mod+Return", keys)
                self.assertIn("Mod+D", keys)
                self.assertEqual(bindings[0].category, "Niri")


class TestKDEParser(unittest.TestCase):
    """Tests for KDEParser with temp INI file."""

    def test_parse_missing_file_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "kglobalshortcutsrc"
            with patch("linta_keybindings.KDE_SHORTCUTS", config):
                parser = linta_keybindings.KDEParser()
                self.assertEqual(parser.parse(), [])

    def test_parse_extracts_shortcuts(self) -> None:
        content = """
[kwin]
KWin = Ctrl+Alt+T,none,Switch One Window Down
krunner = Alt+Space,none,Run command
"""
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "kglobalshortcutsrc"
            config.write_text(content)
            with patch("linta_keybindings.KDE_SHORTCUTS", config):
                parser = linta_keybindings.KDEParser()
                bindings = parser.parse()
                self.assertGreater(len(bindings), 0)
                categories = {b.category for b in bindings}
                self.assertIn("kwin", categories)
                keys = [b.keys for b in bindings]
                self.assertTrue(any("Ctrl" in k or "Alt" in k for k in keys))


class TestModuleConstants(unittest.TestCase):
    """Smoke test: module imports and exposes expected names."""

    def test_key_binding_exported(self) -> None:
        self.assertEqual(linta_keybindings.KeyBinding.__name__, "KeyBinding")

    def test_niri_parser_exported(self) -> None:
        self.assertEqual(linta_keybindings.NiriParser.__name__, "NiriParser")

    def test_kde_parser_exported(self) -> None:
        self.assertEqual(linta_keybindings.KDEParser.__name__, "KDEParser")


class TestOverlayWindow(unittest.TestCase):
    """Tests for overlay display behavior (e.g. missing primary screen)."""

    def test_show_event_handles_missing_primary_screen(self) -> None:
        """showEvent() must not crash when primaryScreen() returns None."""
        window = linta_keybindings.OverlayWindow([])
        with patch("linta_keybindings.QApplication.primaryScreen", return_value=None):
            event = MagicMock()
            window.showEvent(event)


if __name__ == "__main__":
    unittest.main()
