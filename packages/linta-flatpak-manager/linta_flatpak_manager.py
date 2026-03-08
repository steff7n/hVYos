#!/usr/bin/env python3
"""Linta Flatpak Manager — GUI for browsing, installing, and managing Flatpak applications."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable, Optional

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QTextEdit,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
    QFrame,
    QSizePolicy,
)

# Linta palette
BG = "#1e1e2e"
BG_ALT = "#313244"
ACCENT = "#00bcd4"
TEXT = "#cdd6f4"
TEXT_MUTED = "#a6adc8"


@dataclass
class AppInfo:
    """Flatpak application info."""
    name: str
    app_id: str
    version: str = ""
    description: str = ""
    installed: bool = False


class FlatpakWorker(QThread):
    """Worker thread for running flatpak CLI commands."""
    finished = pyqtSignal(bool, str)  # success, output/error
    progress = pyqtSignal(str)

    def __init__(self, args: list[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.args = ["flatpak"] + args

    def run(self) -> None:
        try:
            proc = subprocess.run(
                self.args,
                capture_output=True,
                text=True,
                timeout=600,
            )
            if proc.returncode == 0:
                self.finished.emit(True, proc.stdout or "")
            else:
                self.finished.emit(False, proc.stderr or proc.stdout or "Unknown error")
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Operation timed out")
        except FileNotFoundError:
            self.finished.emit(False, "flatpak not found. Is it installed?")
        except Exception as e:
            self.finished.emit(False, str(e))


def parse_flatpak_columns(output: str) -> list[list[str]]:
    """Parse tab-separated flatpak --columns output."""
    lines = output.strip().split("\n")
    if not lines:
        return []
    rows = []
    for line in lines[1:]:  # skip header
        parts = line.split("\t")
        if parts:
            rows.append(parts)
    return rows


def run_flatpak_sync(args: list[str]) -> tuple[bool, str]:
    """Run flatpak synchronously (for quick queries)."""
    try:
        proc = subprocess.run(
            ["flatpak"] + args,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0:
            return True, proc.stdout or ""
        return False, proc.stderr or proc.stdout or "Unknown error"
    except Exception as e:
        return False, str(e)


class AppItemWidget(QFrame):
    """Single application row in the list."""
    def __init__(self, app: AppInfo, parent: QWidget | None = None):
        super().__init__(parent)
        self.app = app
        self.setObjectName("appItem")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        # Icon placeholder
        icon = QLabel()
        icon.setFixedSize(48, 48)
        icon.setStyleSheet(
            f"background: {BG_ALT}; border-radius: 8px; color: {TEXT_MUTED};"
            " font-size: 24px; qproperty-alignment: AlignCenter;"
        )
        icon.setText("◆")
        layout.addWidget(icon)

        # Name + description
        text_layout = QVBoxLayout()
        name_lbl = QLabel(app.name)
        name_lbl.setStyleSheet(f"color: {TEXT}; font-weight: bold; font-size: 14px;")
        text_layout.addWidget(name_lbl)
        desc = app.description or "No description"
        if len(desc) > 120:
            desc = desc[:117] + "..."
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        text_layout.addWidget(desc_lbl)
        layout.addLayout(text_layout, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        if app.installed:
            perm_btn = QPushButton("Permissions")
            perm_btn.setStyleSheet(
                f"background: {BG_ALT}; color: {TEXT}; border: 1px solid {ACCENT}; border-radius: 4px; padding: 6px 12px;"
            )
            perm_btn.clicked.connect(self._show_permissions)
            btn_layout.addWidget(perm_btn)

            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet(
                f"background: #b34a4a; color: {TEXT}; border: none; border-radius: 4px; padding: 6px 12px;"
            )
            remove_btn.clicked.connect(self._on_remove)
            btn_layout.addWidget(remove_btn)
        else:
            install_btn = QPushButton("Install")
            install_btn.setStyleSheet(
                f"background: {ACCENT}; color: {BG}; border: none; border-radius: 4px; padding: 6px 12px;"
            )
            install_btn.clicked.connect(self._on_install)
            btn_layout.addWidget(install_btn)

        layout.addLayout(btn_layout)

    def _show_permissions(self) -> None:
        ok, out = run_flatpak_sync(["info", "--show-permissions", self.app.app_id])
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Permissions — {self.app.name}")
        dlg.setStyleSheet(f"background: {BG}; color: {TEXT};")
        layout = QVBoxLayout(dlg)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(out if ok else f"Error: {out}")
        te.setStyleSheet(f"background: {BG_ALT}; color: {TEXT}; font-family: monospace;")
        te.setMinimumSize(400, 300)
        layout.addWidget(te)
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(dlg.accept)
        layout.addWidget(btn_box)
        dlg.exec()

    def _on_install(self) -> None:
        parent = self.window()
        if isinstance(parent, QWidget) and hasattr(parent, "install_app"):
            parent.install_app(self.app)

    def _on_remove(self) -> None:
        parent = self.window()
        if isinstance(parent, QWidget) and hasattr(parent, "remove_app"):
            parent.remove_app(self.app)


class LintaFlatpakManager(QWidget):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linta Flatpak Manager")
        self.setMinimumSize(700, 500)
        self.resize(900, 600)
        self._worker: FlatpakWorker | None = None
        self._search_filter = ""

        self._apply_theme()
        self._build_ui()
        self._load_installed()

    def _apply_theme(self) -> None:
        """Apply Linta dark palette and Fusion style."""
        app = QApplication.instance()
        if app:
            app.setStyle("Fusion")
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(BG))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
            palette.setColor(QPalette.ColorRole.Base, QColor(BG_ALT))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BG))
            palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
            palette.setColor(QPalette.ColorRole.Button, QColor(BG_ALT))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(BG))
            app.setPalette(palette)
            app.setStyleSheet(
                f"QWidget {{ background: {BG}; color: {TEXT}; }}"
                f"QLineEdit {{ background: {BG_ALT}; color: {TEXT}; border: 1px solid {ACCENT}; border-radius: 4px; padding: 8px; }}"
                f"QTabWidget::pane {{ background: {BG_ALT}; border: 1px solid {TEXT_MUTED}; border-radius: 4px; }}"
                f"QTabBar::tab {{ background: {BG_ALT}; color: {TEXT}; padding: 10px 20px; margin-right: 2px; }}"
                f"QTabBar::tab:selected {{ background: {ACCENT}; color: {BG}; }}"
                f"QListWidget {{ background: {BG_ALT}; border: none; outline: none; }}"
                f"QListWidget::item {{ border-bottom: 1px solid {BG}; }}"
                f"QScrollArea {{ background: {BG_ALT}; border: none; }}"
            )

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        search = QLineEdit()
        search.setPlaceholderText("Search applications...")
        search.textChanged.connect(self._on_search)
        layout.addWidget(search)

        self.tabs = QTabWidget()
        self.installed_list = QListWidget()
        self.installed_list.setUniformItemSizes(False)
        self.tabs.addTab(self.installed_list, "Installed")

        self.browse_list = QListWidget()
        self.browse_list.setUniformItemSizes(False)
        self.tabs.addTab(self.browse_list, "Browse")

        updates_widget = QWidget()
        updates_layout = QVBoxLayout(updates_widget)
        updates_layout.setContentsMargins(0, 0, 0, 0)
        update_all_btn = QPushButton("Update All")
        update_all_btn.setStyleSheet(
            f"background: {ACCENT}; color: {BG}; border: none; border-radius: 4px; padding: 8px 16px;"
        )
        update_all_btn.clicked.connect(self._update_all)
        updates_layout.addWidget(update_all_btn)
        self.updates_list = QListWidget()
        self.updates_list.setUniformItemSizes(False)
        updates_layout.addWidget(self.updates_list)
        self.tabs.addTab(updates_widget, "Updates")

        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.status_label)

    def _on_search(self, text: str) -> None:
        self._search_filter = text.strip().lower()
        self._refresh_current_tab()

    def _on_tab_changed(self, idx: int) -> None:
        if idx == 0:
            self._load_installed()
        elif idx == 1:
            self._load_browse()
        else:
            self._load_updates()

    def _refresh_current_tab(self) -> None:
        idx = self.tabs.currentIndex()
        if idx == 0:
            self._load_installed()
        elif idx == 1:
            self._load_browse()
        else:
            self._load_updates()

    def _filter_app(self, app: AppInfo) -> bool:
        if not self._search_filter:
            return True
        q = self._search_filter
        return q in app.name.lower() or q in (app.description or "").lower() or q in app.app_id.lower()

    def _populate_list(self, widget: QListWidget, apps: list[AppInfo]) -> None:
        widget.clear()
        for app in apps:
            if not self._filter_app(app):
                continue
            item = QListWidgetItem(widget)
            item_w = AppItemWidget(app)
            item.setSizeHint(item_w.sizeHint())
            widget.addItem(item)
            widget.setItemWidget(item, item_w)

    def _load_installed(self) -> None:
        ok, out = run_flatpak_sync(
            ["list", "--app", "--columns=name,application,version,description"]
        )
        apps: list[AppInfo] = []
        if ok:
            for row in parse_flatpak_columns(out):
                if len(row) >= 2:
                    apps.append(AppInfo(
                        name=row[0],
                        app_id=row[1],
                        version=row[2] if len(row) > 2 else "",
                        description=row[3] if len(row) > 3 else "",
                        installed=True,
                    ))
        self._populate_list(self.installed_list, apps)

    def _load_browse(self) -> None:
        ok, out = run_flatpak_sync(
            ["remote-ls", "flathub", "--app", "--columns=name,application,description"]
        )
        apps: list[AppInfo] = []
        installed_ids: set[str] = set()
        ok2, out2 = run_flatpak_sync(["list", "--app", "--columns=application"])
        if ok2:
            for row in parse_flatpak_columns(out2):
                if row:
                    installed_ids.add(row[0])

        if ok:
            for row in parse_flatpak_columns(out):
                if len(row) >= 2:
                    app_id = row[1]
                    apps.append(AppInfo(
                        name=row[0],
                        app_id=app_id,
                        description=row[2] if len(row) > 2 else "",
                        installed=app_id in installed_ids,
                    ))
        self._populate_list(self.browse_list, apps)

    def _load_updates(self) -> None:
        ok, out = run_flatpak_sync(
            ["list", "--app", "--updates", "--columns=name,application,version"]
        )
        apps: list[AppInfo] = []
        if ok:
            for row in parse_flatpak_columns(out):
                if len(row) >= 2:
                    apps.append(AppInfo(
                        name=row[0],
                        app_id=row[1],
                        version=row[2] if len(row) > 2 else "",
                        installed=True,
                    ))
        self._populate_list(self.updates_list, apps)

    def _run_async(self, args: list[str], on_done: Callable[[bool, str], None]) -> None:
        if self._worker and self._worker.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        self.status_label.setText("Working...")
        self._worker = FlatpakWorker(args)
        self._worker.finished.connect(on_done)

        def cleanup(success: bool, msg: str) -> None:
            self._worker = None
            self.status_label.setText("")

        self._worker.finished.connect(cleanup)
        self._worker.start()

    def install_app(self, app: AppInfo) -> None:
        def done(success: bool, msg: str) -> None:
            if success:
                QMessageBox.information(self, "Install", f"{app.name} installed successfully.")
                self._refresh_current_tab()
            else:
                QMessageBox.critical(self, "Install Failed", msg)

        self._run_async(["install", "-y", "flathub", app.app_id], done)

    def remove_app(self, app: AppInfo) -> None:
        reply = QMessageBox.question(
            self,
            "Remove",
            f"Remove {app.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def done(success: bool, msg: str) -> None:
            if success:
                QMessageBox.information(self, "Remove", f"{app.name} removed.")
                self._refresh_current_tab()
            else:
                QMessageBox.critical(self, "Remove Failed", msg)

        self._run_async(["uninstall", "-y", app.app_id], done)

    def _update_all(self) -> None:
        def done(success: bool, msg: str) -> None:
            if success:
                QMessageBox.information(self, "Update", "All applications updated.")
                self._load_updates()
            else:
                QMessageBox.critical(self, "Update Failed", msg)

        self._run_async(["update", "-y"], done)


def main() -> None:
    import sys
    app = QApplication(sys.argv)
    w = LintaFlatpakManager()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
