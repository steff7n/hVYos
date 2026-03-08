#!/usr/bin/env python3
"""linta-welcome — Linta Linux first-boot welcome application.

A PyQt6 wizard shown on first boot. Guides the user through:
1. Terminal emulator selection (with visual previews)
2. File manager selection (with visual previews)
3. Font wizard (4 preset tiers + manual override)
4. Theme picker (rice presets or KDE theme)
5. Timezone/locale confirmation
6. Quick tips

Can also be invoked standalone for individual steps:
  linta-welcome                  Full wizard
  linta-welcome --font-wizard-only   Font wizard only (for lintactl re-run)

Profiles: [KDE], [Niri], [Combined]
Spec reference: README.md §10.2
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup, QGroupBox,
    QCheckBox, QComboBox, QLineEdit, QScrollArea, QWidget,
    QGridLayout, QFrame, QSizePolicy, QMessageBox,
)

VERSION = "0.1.0"
RELEASE_FILE = Path("/etc/linta-release")
THEMES_DIR = Path("/usr/share/linta/themes")
FIRST_BOOT_MARKER = Path("/var/lib/linta/first-boot-done")


def _get_profile() -> str:
    if RELEASE_FILE.exists():
        for line in RELEASE_FILE.read_text().splitlines():
            if line.startswith("VARIANT_ID="):
                return line.split("=", 1)[1].strip().strip('"')
    return "kde"


def _run(cmd: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _install_packages(packages: list[str]) -> bool:
    """Install packages via DNF."""
    if not packages:
        return True
    try:
        result = _run(["pkexec", "dnf", "install", "-y"] + packages, check=True)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _dark_palette() -> QPalette:
    """Create a dark palette matching the Linta identity."""
    palette = QPalette()
    bg = QColor(30, 30, 46)
    bg_alt = QColor(40, 40, 64)
    fg = QColor(205, 214, 244)
    accent = QColor(0, 188, 212)
    dim = QColor(108, 112, 134)

    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, fg)
    palette.setColor(QPalette.ColorRole.Base, bg_alt)
    palette.setColor(QPalette.ColorRole.AlternateBase, bg)
    palette.setColor(QPalette.ColorRole.Text, fg)
    palette.setColor(QPalette.ColorRole.Button, bg_alt)
    palette.setColor(QPalette.ColorRole.ButtonText, fg)
    palette.setColor(QPalette.ColorRole.Highlight, accent)
    palette.setColor(QPalette.ColorRole.HighlightedText, bg)
    palette.setColor(QPalette.ColorRole.PlaceholderText, dim)
    return palette


class OptionCard(QFrame):
    """A selectable card widget for option lists."""

    def __init__(self, name: str, description: str, icon_text: str = "",
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.name = name
        self._selected = False

        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        if icon_text:
            icon_label = QLabel(icon_text)
            icon_label.setFont(QFont("JetBrains Mono", 18))
            icon_label.setFixedWidth(40)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        text_layout.addWidget(name_label)

        desc_label = QLabel(description)
        desc_label.setFont(QFont("JetBrains Mono", 10))
        desc_label.setStyleSheet("color: #6c7086;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, 1)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._update_style()

    def _update_style(self) -> None:
        if self._selected:
            self.setStyleSheet(
                "OptionCard { background: #282840; border: 2px solid #00bcd4; border-radius: 8px; }"
            )
        else:
            self.setStyleSheet(
                "OptionCard { background: #1e1e2e; border: 1px solid #45475a; border-radius: 8px; }"
                "OptionCard:hover { border: 1px solid #6c7086; }"
            )

    def mousePressEvent(self, event: Any) -> None:
        self.clicked_signal()
        super().mousePressEvent(event)

    def clicked_signal(self) -> None:
        pass  # overridden by connection logic


class SelectionPage(QWizardPage):
    """Base page for selecting from a list of options."""

    def __init__(self, title: str, subtitle: str, options: list[dict[str, str]],
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle(title)
        self.setSubTitle(subtitle)
        self.selected_option: str = ""
        self.cards: list[OptionCard] = []

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        card_layout = QVBoxLayout(container)
        card_layout.setSpacing(8)

        for opt in options:
            card = OptionCard(
                opt["name"], opt["description"], opt.get("icon", "")
            )
            card.clicked_signal = lambda n=opt["name"]: self._select(n)
            card_layout.addWidget(card)
            self.cards.append(card)

            if opt.get("default"):
                self._select(opt["name"])

        card_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _select(self, name: str) -> None:
        self.selected_option = name
        for card in self.cards:
            card.set_selected(card.name == name)
        self.completeChanged.emit()

    def isComplete(self) -> bool:
        return bool(self.selected_option)


class TerminalPage(SelectionPage):
    """Terminal emulator selection."""

    TERMINALS = [
        {"name": "WezTerm", "package": "wezterm",
         "description": "GPU-accelerated, multiplexer built-in, Lua config (recommended)",
         "icon": ">_", "default": True},
        {"name": "Alacritty", "package": "alacritty",
         "description": "GPU-accelerated, minimal, TOML config",
         "icon": ">_"},
        {"name": "Kitty", "package": "kitty",
         "description": "GPU-accelerated, image support, Python extensions",
         "icon": ">_"},
        {"name": "foot", "package": "foot",
         "description": "Wayland-native, lightweight, fast startup",
         "icon": ">_"},
        {"name": "Ghostty", "package": "ghostty",
         "description": "Native platform UI, GPU-accelerated, Zig-based",
         "icon": ">_"},
        {"name": "Tilix", "package": "tilix",
         "description": "GTK tiling terminal, D-Bus integration",
         "icon": ">_"},
        {"name": "Terminator", "package": "terminator",
         "description": "GTK, multiple panes, layout persistence",
         "icon": ">_"},
    ]

    def __init__(self, parent: QWidget | None = None):
        super().__init__(
            "Terminal Emulator",
            "Choose your default terminal emulator. "
            "Only the selected terminal will be installed.",
            self.TERMINALS,
            parent,
        )

    def get_package(self) -> str:
        for t in self.TERMINALS:
            if t["name"] == self.selected_option:
                return t["package"]
        return ""


class FileManagerPage(SelectionPage):
    """File manager selection."""

    def __init__(self, profile: str, parent: QWidget | None = None):
        options = self._get_options(profile)
        super().__init__(
            "File Manager",
            "Choose your file manager. Only the selected one will be installed.",
            options,
            parent,
        )
        self._options = options

    @staticmethod
    def _get_options(profile: str) -> list[dict[str, str]]:
        graphical = [
            {"name": "Dolphin", "package": "dolphin",
             "description": "KDE's file manager — tabs, split view, terminal panel",
             "icon": "D", "default": profile == "kde"},
            {"name": "Thunar", "package": "thunar",
             "description": "XFCE's file manager — lightweight, plugin-based",
             "icon": "T"},
            {"name": "Nautilus", "package": "nautilus",
             "description": "GNOME Files — clean, modern, GTK",
             "icon": "N"},
            {"name": "PCManFM-Qt", "package": "pcmanfm-qt",
             "description": "Lightweight Qt file manager, tabbed interface",
             "icon": "P"},
            {"name": "nnn", "package": "nnn",
             "description": "Terminal file manager — blazing fast, plugin ecosystem",
             "icon": "n", "default": profile == "niri"},
            {"name": "ranger", "package": "ranger",
             "description": "Terminal file manager — vim keybindings, preview pane",
             "icon": "r"},
            {"name": "yazi", "package": "yazi",
             "description": "Terminal file manager — async I/O, image preview, Rust",
             "icon": "y"},
        ]
        return graphical

    def get_package(self) -> str:
        for o in self._options:
            if o["name"] == self.selected_option:
                return o["package"]
        return ""


class FontWizardPage(QWizardPage):
    """Font selection wizard with preset tiers."""

    PRESETS = {
        "Comprehensive": {
            "description": "All fonts commonly shipped by major distributions — "
                          "Latin, CJK, Arabic, Cyrillic, emoji, monospace",
            "packages": [
                "google-noto-sans-fonts", "google-noto-serif-fonts",
                "google-noto-mono-fonts", "google-noto-emoji-fonts",
                "google-noto-cjk-fonts-common", "google-noto-sans-cjk-ttc-fonts",
                "google-noto-sans-arabic-fonts", "liberation-fonts",
                "dejavu-sans-fonts", "dejavu-serif-fonts", "dejavu-sans-mono-fonts",
                "jetbrains-mono-fonts-all", "fira-code-fonts",
                "ibm-plex-mono-fonts", "ibm-plex-sans-fonts",
                "mozilla-fira-sans-fonts",
            ],
        },
        "Standard": {
            "description": "Major Latin families, one CJK set, emoji, one monospace. "
                          "Covers most use cases.",
            "packages": [
                "google-noto-sans-fonts", "google-noto-serif-fonts",
                "google-noto-emoji-fonts", "google-noto-sans-cjk-ttc-fonts",
                "dejavu-sans-fonts", "dejavu-serif-fonts", "dejavu-sans-mono-fonts",
                "jetbrains-mono-fonts-all", "liberation-fonts",
            ],
        },
        "Per-Locale": {
            "description": "Fonts relevant to your selected locale(s) + emoji + monospace.",
            "packages": [
                "google-noto-sans-fonts", "google-noto-emoji-fonts",
                "dejavu-sans-fonts", "dejavu-sans-mono-fonts",
                "jetbrains-mono-fonts-all",
            ],
        },
        "Bare Minimum": {
            "description": "Only system-critical fonts required for correct UI rendering.",
            "packages": [
                "dejavu-sans-fonts", "dejavu-sans-mono-fonts",
                "google-noto-emoji-fonts",
            ],
        },
    }

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle("Font Selection")
        self.setSubTitle("Choose a font preset. You can adjust individual fonts after installation.")
        self.selected_preset = "Comprehensive"

        layout = QVBoxLayout(self)

        self.btn_group = QButtonGroup(self)
        for i, (name, info) in enumerate(self.PRESETS.items()):
            radio = QRadioButton(f"{name}")
            radio.setFont(QFont("JetBrains Mono", 11))
            if i == 0:
                radio.setChecked(True)
            self.btn_group.addButton(radio, i)
            layout.addWidget(radio)

            desc = QLabel(f"  {info['description']}")
            desc.setStyleSheet("color: #6c7086; margin-bottom: 8px;")
            desc.setWordWrap(True)
            desc.setFont(QFont("JetBrains Mono", 9))
            layout.addWidget(desc)

            pkg_count = len(info["packages"])
            count_label = QLabel(f"  {pkg_count} package{'s' if pkg_count != 1 else ''}")
            count_label.setStyleSheet("color: #45475a; margin-bottom: 16px;")
            count_label.setFont(QFont("JetBrains Mono", 9))
            layout.addWidget(count_label)

        self.btn_group.idToggled.connect(self._on_preset_changed)
        layout.addStretch()

    def _on_preset_changed(self, id: int, checked: bool) -> None:
        if checked:
            self.selected_preset = list(self.PRESETS.keys())[id]

    def get_packages(self) -> list[str]:
        return self.PRESETS[self.selected_preset]["packages"]


class ThemePickerPage(SelectionPage):
    """Theme/rice selection."""

    def __init__(self, profile: str, parent: QWidget | None = None):
        options = self._get_options(profile)
        super().__init__(
            "Theme",
            "Choose your visual theme. You can switch themes later with 'lintactl theme set'.",
            options,
            parent,
        )

    @staticmethod
    def _get_options(profile: str) -> list[dict[str, str]]:
        options = []

        if profile in ("kde", "combined"):
            options.append({
                "name": "Linta (KDE)",
                "description": "Dark theme with teal accent — Linta's signature look",
                "icon": "K", "default": profile == "kde",
            })
            options.append({
                "name": "Breeze",
                "description": "KDE's default theme — familiar and polished",
                "icon": "B",
            })

        if profile in ("niri", "combined"):
            options.extend([
                {"name": "Dusk", "description": "Warm dark — deep navy with amber accents",
                 "icon": "1", "default": profile == "niri"},
                {"name": "Frost", "description": "Cool dark — midnight with ice blue accents",
                 "icon": "2"},
                {"name": "Forest", "description": "Earthy dark — green tones with emerald accents",
                 "icon": "3"},
                {"name": "Ember", "description": "High-contrast dark — charcoal with orange accents",
                 "icon": "4"},
                {"name": "Vanilla Niri", "description": "Stock Niri defaults — no custom theming",
                 "icon": "V"},
            ])

        return options


class LocalePage(QWizardPage):
    """Timezone and locale confirmation."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle("System Configuration")
        self.setSubTitle("Confirm your timezone and locale settings.")

        layout = QVBoxLayout(self)

        # Timezone
        tz_group = QGroupBox("Timezone")
        tz_layout = QHBoxLayout(tz_group)
        self.tz_combo = QComboBox()
        self.tz_combo.setEditable(True)
        self.tz_combo.setFont(QFont("JetBrains Mono", 11))

        timezones = self._get_timezones()
        self.tz_combo.addItems(timezones)

        current_tz = self._get_current_tz()
        idx = self.tz_combo.findText(current_tz)
        if idx >= 0:
            self.tz_combo.setCurrentIndex(idx)

        tz_layout.addWidget(self.tz_combo)
        layout.addWidget(tz_group)

        # Locale
        locale_group = QGroupBox("Locale")
        locale_layout = QHBoxLayout(locale_group)
        self.locale_combo = QComboBox()
        self.locale_combo.setFont(QFont("JetBrains Mono", 11))
        self.locale_combo.addItems([
            "en_US.UTF-8", "en_GB.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8",
            "es_ES.UTF-8", "it_IT.UTF-8", "pt_BR.UTF-8", "pl_PL.UTF-8",
            "ja_JP.UTF-8", "ko_KR.UTF-8", "zh_CN.UTF-8", "ru_RU.UTF-8",
        ])
        locale_layout.addWidget(self.locale_combo)
        layout.addWidget(locale_group)

        layout.addStretch()

    @staticmethod
    def _get_timezones() -> list[str]:
        try:
            result = _run(["timedatectl", "list-timezones"])
            if result.returncode == 0:
                return result.stdout.strip().splitlines()
        except FileNotFoundError:
            pass
        return ["UTC", "America/New_York", "Europe/London", "Europe/Warsaw",
                "Asia/Tokyo", "Asia/Shanghai"]

    @staticmethod
    def _get_current_tz() -> str:
        try:
            result = _run(["timedatectl", "show", "-p", "Timezone", "--value"])
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        return "UTC"


class QuickTipsPage(QWizardPage):
    """Non-intrusive overview of Linta features."""

    def __init__(self, profile: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle("Quick Tips")
        self.setSubTitle("A few things that make Linta different.")

        layout = QVBoxLayout(self)

        tips = [
            ("Transactional updates",
             "Every package operation creates a Btrfs snapshot. "
             "If something breaks, roll back from the GRUB menu."),
            ("Snapshot management",
             "Run 'linta-snapshots list' to see snapshots, "
             "'linta-snapshots rollback <n>' to restore."),
            ("Theme switching",
             "Run 'lintactl theme list' and 'lintactl theme set <name>' "
             "to change your visual theme anytime."),
            ("NVIDIA GPU",
             "Run 'sudo linta-nvidia setup' to install and configure "
             "NVIDIA proprietary drivers with Wayland support."),
            ("Software",
             "System packages: dnf. Additional apps: Flatpak (Flathub). "
             "Run 'lintactl info' for system details."),
        ]

        if profile in ("niri", "combined"):
            tips.append((
                "Niri keybindings",
                "Mod+Return: terminal, Mod+D: launcher, Mod+Q: close, "
                "Mod+Shift+/: show all keybindings."
            ))

        for title, desc in tips:
            tip_frame = QFrame()
            tip_frame.setStyleSheet(
                "QFrame { background: #282840; border-radius: 8px; padding: 12px; }"
            )
            tip_layout = QVBoxLayout(tip_frame)
            tip_layout.setContentsMargins(12, 8, 12, 8)

            title_label = QLabel(title)
            title_label.setFont(QFont("JetBrains Mono", 11, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #00bcd4;")
            tip_layout.addWidget(title_label)

            desc_label = QLabel(desc)
            desc_label.setFont(QFont("JetBrains Mono", 10))
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #cdd6f4;")
            tip_layout.addWidget(desc_label)

            layout.addWidget(tip_frame)

        layout.addStretch()


class LintaWelcomeWizard(QWizard):
    """Main welcome wizard."""

    def __init__(self, font_wizard_only: bool = False):
        super().__init__()
        self.profile = _get_profile()
        self.font_wizard_only = font_wizard_only

        self.setWindowTitle("Welcome to Linta")
        self.setMinimumSize(QSize(700, 550))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        if font_wizard_only:
            self.font_page = FontWizardPage()
            self.addPage(self.font_page)
        else:
            self.terminal_page = TerminalPage()
            self.file_manager_page = FileManagerPage(self.profile)
            self.font_page = FontWizardPage()
            self.theme_page = ThemePickerPage(self.profile)
            self.locale_page = LocalePage()
            self.tips_page = QuickTipsPage(self.profile)

            self.addPage(self._make_welcome_page())
            self.addPage(self.terminal_page)
            self.addPage(self.file_manager_page)
            self.addPage(self.font_page)
            self.addPage(self.theme_page)
            self.addPage(self.locale_page)
            self.addPage(self.tips_page)

    def _make_welcome_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Welcome to Linta")
        layout = QVBoxLayout(page)
        layout.addStretch()

        title = QLabel("Linta")
        title.setFont(QFont("JetBrains Mono", 36, QFont.Weight.Bold))
        title.setStyleSheet("color: #00bcd4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Lean by design.")
        subtitle.setFont(QFont("JetBrains Mono", 14))
        subtitle.setStyleSheet("color: #6c7086;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        desc = QLabel(
            "This wizard will set up your terminal, file manager, fonts, and theme.\n"
            "Each choice installs only what you select — nothing extra."
        )
        desc.setFont(QFont("JetBrains Mono", 11))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()
        return page

    def accept(self) -> None:
        """Apply selections when wizard finishes."""
        packages_to_install: list[str] = []

        if not self.font_wizard_only:
            # Terminal
            pkg = self.terminal_page.get_package()
            if pkg:
                packages_to_install.append(pkg)

            # File manager
            pkg = self.file_manager_page.get_package()
            if pkg:
                packages_to_install.append(pkg)

        # Fonts
        packages_to_install.extend(self.font_page.get_packages())

        if packages_to_install:
            _install_packages(packages_to_install)

        if not self.font_wizard_only and hasattr(self, "theme_page"):
            theme = self.theme_page.selected_option
            if theme:
                self._apply_theme(theme)

        # Mark first boot as done
        FIRST_BOOT_MARKER.parent.mkdir(parents=True, exist_ok=True)
        FIRST_BOOT_MARKER.write_text("done\n")

        super().accept()

    def _apply_theme(self, theme_name: str) -> None:
        theme_map = {
            "Dusk": "linta-niri-rice-1",
            "Frost": "linta-niri-rice-2",
            "Forest": "linta-niri-rice-3",
            "Ember": "linta-niri-rice-4",
            "Linta (KDE)": "linta-kde-default",
        }
        theme_id = theme_map.get(theme_name, "")
        if theme_id:
            _run(["lintactl", "theme", "set", theme_id])


def main() -> None:
    parser = argparse.ArgumentParser(prog="linta-welcome")
    parser.add_argument("--version", action="version", version=f"linta-welcome {VERSION}")
    parser.add_argument("--font-wizard-only", action="store_true",
                        help="Run only the font wizard (for lintactl font-wizard)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("Linta Welcome")
    app.setStyle("Fusion")
    app.setPalette(_dark_palette())
    app.setFont(QFont("JetBrains Mono", 10))

    wizard = LintaWelcomeWizard(font_wizard_only=args.font_wizard_only)
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
