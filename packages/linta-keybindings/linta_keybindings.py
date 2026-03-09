#!/usr/bin/env python3
"""linta-keybindings — Searchable keybinding reference overlay for Linta Linux.

A rofi-style frameless overlay that displays keybindings for the current
desktop (KDE Plasma or Niri). Parses configs or uses hardcoded Linta bindings.

Profiles: [KDE], [Niri], [Combined]
Spec reference: README.md §9.4
"""

from __future__ import annotations

import os
import re
import configparser
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)

BG_COLOR = "#1e1e2e"
ACCENT_COLOR = "#00bcd4"
OPACITY = 0.95
FONT_FAMILY = "JetBrains Mono"

CONFIG_HOME = Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")))
NIRI_CONFIG = CONFIG_HOME / "niri" / "config.kdl"
KDE_SHORTCUTS = CONFIG_HOME / "kglobalshortcutsrc"


@dataclass
class KeyBinding:
    """A single keybinding with category, keys, and description."""

    category: str
    keys: str
    description: str


def _detect_desktop() -> str:
    """Detect current desktop from XDG_CURRENT_DESKTOP."""
    xdg = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "niri" in xdg or "niri" in os.environ.get("XDG_SESSION_TYPE", "").lower():
        return "niri"
    if "kde" in xdg or "plasma" in xdg:
        return "kde"
    return "niri" if "niri" in xdg else "kde"


class NiriParser:
    """Parse Niri config.kdl to extract keybindings from binds blocks."""

    def parse(self) -> list[KeyBinding]:
        bindings: list[KeyBinding] = []
        if not NIRI_CONFIG.exists():
            return bindings

        content = NIRI_CONFIG.read_text()
        # Match: binds { ... } — may be nested; we want top-level binds
        binds_match = re.search(r"\bbinds\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", content)
        if not binds_match:
            return bindings

        block = binds_match.group(1)
        # Each line: Mod+Return { spawn "term"; } or Mod+T repeat=false { action; }
        line_re = re.compile(
            r"(\S+)(?:\s+[a-zA-Z0-9_-]+=[^\s]+)*\s*\{([^}]+)\}"
        )
        for m in line_re.finditer(block):
            keys = m.group(1)
            action = m.group(2).strip().rstrip(";").strip()
            # Simplify spawn "cmd" to "Launch cmd"
            spawn_m = re.match(r'spawn\s+"([^"]+)"', action)
            if spawn_m:
                desc = f"Launch {spawn_m.group(1).split()[0]}"
            else:
                desc = action.replace("-", " ").replace(";", " ")
            bindings.append(KeyBinding(category="Niri", keys=keys, description=desc))

        return bindings


class KDEParser:
    """Parse KDE kglobalshortcutsrc (INI) to extract keybindings."""

    def parse(self) -> list[KeyBinding]:
        bindings: list[KeyBinding] = []
        if not KDE_SHORTCUTS.exists():
            return bindings

        config = configparser.RawConfigParser()
        try:
            config.read(KDE_SHORTCUTS)
        except configparser.Error:
            return bindings

        skip_keys = {"_k_friendly_name"}
        for section in config.sections():
            if section.startswith("$"):
                continue
            for key, value in config.items(section):
                if key in skip_keys:
                    continue
                parts = [p.strip() for p in value.split(",", 2)]
                primary = parts[0] if len(parts) > 0 else "none"
                secondary = parts[1] if len(parts) > 1 else "none"
                desc = parts[2] if len(parts) > 2 else key
                shortcut = primary if primary != "none" else secondary
                if shortcut == "none" or not shortcut:
                    continue
                # Use section as category (e.g., kwin, krunner)
                category = section
                bindings.append(KeyBinding(category=category, keys=shortcut, description=desc))

        return bindings


def _linta_bindings() -> list[KeyBinding]:
    """Hardcoded Linta-specific keybindings."""
    return [
        KeyBinding(
            category="Linta",
            keys="Mod+Shift+/",
            description="Open keybinding reference overlay",
        ),
    ]


class OverlayWindow(QWidget):
    """Frameless semi-transparent overlay showing filtered keybindings."""

    def __init__(self, bindings: list[KeyBinding]) -> None:
        super().__init__()
        self.bindings = bindings
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search keybindings...")
        self.search.textChanged.connect(self._filter_list)
        layout.addWidget(self.search)

        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.list_widget.keyPressEvent = self._list_key_handler
        layout.addWidget(self.list_widget)

        self._populate_list(self.bindings)
        self.search.setFocus()

    def _apply_theme(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_COLOR};
                color: #cdd6f4;
                font-family: "{FONT_FAMILY}";
            }}
            QLineEdit {{
                background-color: #313244;
                border: 2px solid {ACCENT_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                color: #cdd6f4;
                font-size: 14px;
            }}
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 188, 212, 0.3);
            }}
            QListWidget::item:hover {{
                background-color: rgba(0, 188, 212, 0.15);
            }}
        """)
        self.setWindowOpacity(OPACITY)

    def _populate_list(self, bindings: list[KeyBinding]) -> None:
        self.list_widget.clear()
        by_category: dict[str, list[KeyBinding]] = defaultdict(list)
        for b in bindings:
            by_category[b.category].append(b)
        for cat in sorted(by_category.keys()):
            header = QListWidgetItem(f"  ── {cat} ──")
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            header.setForeground(QColor(ACCENT_COLOR))
            self.list_widget.addItem(header)
            for b in sorted(by_category[cat], key=lambda x: x.keys):
                item = QListWidgetItem(f"  {b.keys:<24}  {b.description}")
                item.setData(Qt.ItemDataRole.UserRole, b)
                self.list_widget.addItem(item)

    def _filter_list(self) -> None:
        q = self.search.text().strip().lower()
        if not q:
            self._populate_list(self.bindings)
            return
        filtered = [
            b for b in self.bindings
            if q in b.keys.lower() or q in b.description.lower() or q in b.category.lower()
        ]
        self._populate_list(filtered)

    def _list_key_handler(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        QListWidget.keyPressEvent(self.list_widget, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            return
        super().keyPressEvent(event)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.primaryScreen()
        if screen is not None:
            rect = screen.availableGeometry()
            self.setFixedSize(600, 500)
            self.move(
                rect.x() + (rect.width() - self.width()) // 2,
                rect.y() + (rect.height() - self.height()) // 2,
            )
        else:
            self.setFixedSize(600, 500)
            self.move(0, 0)

    def focusOutEvent(self, event) -> None:
        # Close when focus leaves our window (e.g. user clicked outside)
        def check_focus() -> None:
            if self.isVisible():
                nw = QApplication.focusWidget()
                if nw is None or not self.isAncestorOf(nw):
                    self.close()

        if event.reason() != Qt.FocusReason.PopupFocusReason:
            QTimer.singleShot(0, check_focus)
        super().focusOutEvent(event)


def main() -> None:
    desktop = _detect_desktop()
    bindings: list[KeyBinding] = _linta_bindings()

    if desktop == "niri":
        bindings.extend(NiriParser().parse())
    else:
        bindings.extend(KDEParser().parse())

    app = QApplication([])
    win = OverlayWindow(bindings)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
