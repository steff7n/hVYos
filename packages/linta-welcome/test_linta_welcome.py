#!/usr/bin/env python3
"""Unit tests for linta-welcome."""

from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

import linta_welcome


class TestWelcomeWizard(unittest.TestCase):
    """Tests for the welcome wizard accept flow."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_accept_does_not_crash_when_marker_write_is_denied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocked_dir = Path(tmp) / "blocked"
            blocked_dir.mkdir()
            blocked_dir.chmod(stat.S_IREAD | stat.S_IEXEC)

            wizard = linta_welcome.LintaWelcomeWizard(font_wizard_only=True)
            wizard.font_page.get_packages = lambda: []

            with patch("linta_welcome.FIRST_BOOT_MARKER", blocked_dir / "first-boot-done"), patch(
                "linta_welcome.QWizard.accept"
            ) as mock_super_accept:
                wizard.accept()

            mock_super_accept.assert_called_once()


if __name__ == "__main__":
    unittest.main()
