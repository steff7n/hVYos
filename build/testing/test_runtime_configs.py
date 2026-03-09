#!/usr/bin/env python3
"""Static consistency checks for shipped runtime configs and specs."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestThemeAndConfigConsistency(unittest.TestCase):
    """Tests for shipped theme/config consistency."""

    def test_waybar_memory_uses_percentage_placeholder(self) -> None:
        designer = (REPO_ROOT / "scripts" / "theme-designer" / "designer.js").read_text()
        rice2 = (REPO_ROOT / "themes" / "niri" / "rice-2" / "waybar" / "config.jsonc").read_text()
        rice4 = (REPO_ROOT / "themes" / "niri" / "rice-4" / "waybar" / "config.jsonc").read_text()

        self.assertIn("{percentage}%", designer)
        self.assertIn("{percentage}%", rice2)
        self.assertIn("{percentage}%", rice4)
        self.assertNotIn("{}%", rice2)
        self.assertNotIn("{}%", rice4)

    def test_sddm_theme_does_not_reference_missing_background_asset(self) -> None:
        main_qml = (REPO_ROOT / "themes" / "sddm" / "Main.qml").read_text()
        theme_conf = (REPO_ROOT / "themes" / "sddm" / "theme.conf").read_text()
        metadata = (REPO_ROOT / "themes" / "sddm" / "metadata.desktop").read_text()
        background = REPO_ROOT / "themes" / "sddm" / "background.png"

        if background.exists():
            self.assertIn("background.png", main_qml)
            self.assertIn("background.png", theme_conf)
            self.assertIn("background.png", metadata)
        else:
            self.assertNotIn("background.png", main_qml)
            self.assertNotIn("background.png", theme_conf)
            self.assertNotIn("background.png", metadata)

    def test_niri_terminal_dependency_matches_configs(self) -> None:
        niri_packages = (REPO_ROOT / "build" / "packages" / "niri.txt").read_text()
        niri_kickstart = (REPO_ROOT / "build" / "kickstart" / "linta-niri.ks").read_text()
        combined_kickstart = (REPO_ROOT / "build" / "kickstart" / "linta-combined.ks").read_text()
        niri_config = (REPO_ROOT / "configs" / "niri" / "config.kdl").read_text()
        fuzzel = (REPO_ROOT / "themes" / "niri" / "rice-1" / "fuzzel" / "fuzzel.ini").read_text()

        self.assertIn('spawn "foot"', niri_config)
        self.assertIn("terminal=foot", fuzzel)
        self.assertIn("foot", niri_packages)
        self.assertIn("foot", niri_kickstart)
        self.assertIn("foot", combined_kickstart)

    def test_niri_configs_do_not_reference_missing_wallpaper_path(self) -> None:
        niri_config = (REPO_ROOT / "configs" / "niri" / "config.kdl").read_text()
        niri_kickstart = (REPO_ROOT / "build" / "kickstart" / "linta-niri.ks").read_text()
        combined_kickstart = (REPO_ROOT / "build" / "kickstart" / "linta-combined.ks").read_text()

        missing_path = "/usr/share/backgrounds/linta/default.png"
        self.assertNotIn(missing_path, niri_config)
        self.assertNotIn(missing_path, niri_kickstart)
        self.assertNotIn(missing_path, combined_kickstart)


class TestPackageManifestConsistency(unittest.TestCase):
    """Tests for package/spec naming consistency."""

    def test_linta_custom_manifest_uses_real_niri_theme_package_name(self) -> None:
        manifest = (REPO_ROOT / "build" / "packages" / "linta-custom.txt").read_text()

        self.assertIn("linta-theme-niri", manifest)
        self.assertNotIn("linta-theme-niri-rice1", manifest)
        self.assertNotIn("linta-theme-niri-rice2", manifest)
        self.assertNotIn("linta-theme-niri-rice3", manifest)
        self.assertNotIn("linta-theme-niri-rice4", manifest)

    def test_snapshot_spec_does_not_require_uninstalled_pycache(self) -> None:
        spec = (REPO_ROOT / "packages" / "linta-snapshots" / "linta-snapshots.spec").read_text()
        self.assertNotIn("__pycache__", spec)


if __name__ == "__main__":
    unittest.main()
