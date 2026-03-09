#!/usr/bin/env python3
"""Unit tests for linta-keybindings."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QApplication

import linta_keybindings


class TestOverlayWindow(unittest.TestCase):
    """Tests for overlay display behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_show_event_handles_missing_primary_screen(self) -> None:
        window = linta_keybindings.OverlayWindow([])
        with patch("linta_keybindings.QApplication.primaryScreen", return_value=None):
            window.showEvent(QShowEvent())


if __name__ == "__main__":
    unittest.main()
