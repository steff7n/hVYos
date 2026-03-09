#!/usr/bin/env python3
"""Unit tests for linta-nvidia."""

import argparse
import unittest
from pathlib import Path
from unittest import mock

import linta_nvidia
from linta_nvidia import (
    GpuInfo,
    NvidiaStatus,
    RELEASE_FILE,
    _determine_driver_branch,
    _enable_rpm_fusion,
    _get_profile,
    build_parser,
    detect_gpus,
    get_nvidia_driver_version,
)


# --- Test 1: GpuInfo dataclass creation ---
class TestGpuInfo(unittest.TestCase):
    def test_gpuinfo_creation(self):
        gpu = GpuInfo(
            pci_slot="0000:01:00.0",
            vendor="NVIDIA",
            model="GA106M [GeForce RTX 3060 Mobile]",
            driver="nvidia",
            pci_id="10de:2520",
            is_nvidia=True,
        )
        self.assertEqual(gpu.pci_slot, "0000:01:00.0")
        self.assertEqual(gpu.vendor, "NVIDIA")
        self.assertEqual(gpu.model, "GA106M [GeForce RTX 3060 Mobile]")
        self.assertEqual(gpu.driver, "nvidia")
        self.assertEqual(gpu.pci_id, "10de:2520")
        self.assertTrue(gpu.is_nvidia)


# --- Test 2: NvidiaStatus defaults ---
class TestNvidiaStatus(unittest.TestCase):
    def test_nvidia_status_defaults(self):
        status = NvidiaStatus()
        self.assertEqual(status.gpus, [])
        self.assertEqual(status.driver_version, "")
        self.assertEqual(status.driver_package, "")
        self.assertFalse(status.is_hybrid)
        self.assertEqual(status.integrated_gpu, "")
        self.assertFalse(status.wayland_ready)
        self.assertEqual(status.profile, "")


# --- Test 3, 4, 5: detect_gpus variants ---
LSPCI_NVIDIA_ONLY = """0000:01:00.0 VGA compatible controller: NVIDIA Corporation GA106M [GeForce RTX 3060 Mobile] [10de:2520]
"""

LSPCI_INTEL_ONLY = """0000:00:02.0 VGA compatible controller: Intel Corporation TigerLake-H GT1 [UHD Graphics] [8086:9a60]
"""

LSPCI_HYBRID = """0000:01:00.0 VGA compatible controller: NVIDIA Corporation GA106M [GeForce RTX 3060 Mobile] [10de:2520]
0000:00:02.0 VGA compatible controller: Intel Corporation TigerLake-H GT1 [UHD Graphics] [8086:9a60]
"""


def _make_proc(stdout: str, returncode: int = 0):
    proc = mock.MagicMock()
    proc.stdout = stdout
    proc.stderr = ""
    proc.returncode = returncode
    return proc


class TestDetectGpus(unittest.TestCase):
    @mock.patch("linta_nvidia._run")
    def test_detect_gpus_nvidia_only(self, mock_run):
        def run_side_effect(cmd, check=True):
            if cmd == ["lspci", "-nn", "-D"]:
                return _make_proc(LSPCI_NVIDIA_ONLY)
            if cmd[:3] == ["lspci", "-k", "-s"]:
                return _make_proc("	Kernel driver in use: nvidia\n")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        gpus = detect_gpus()
        self.assertEqual(len(gpus), 1)
        self.assertEqual(gpus[0].pci_slot, "0000:01:00.0")
        self.assertEqual(gpus[0].vendor, "NVIDIA")
        self.assertTrue(gpus[0].is_nvidia)
        self.assertEqual(gpus[0].driver, "nvidia")
        self.assertEqual(gpus[0].pci_id, "10de:2520")

    @mock.patch("linta_nvidia._run")
    def test_detect_gpus_intel_only(self, mock_run):
        def run_side_effect(cmd, check=True):
            if cmd == ["lspci", "-nn", "-D"]:
                return _make_proc(LSPCI_INTEL_ONLY)
            if cmd[:3] == ["lspci", "-k", "-s"]:
                return _make_proc("	Kernel driver in use: i915\n")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        gpus = detect_gpus()
        self.assertEqual(len(gpus), 1)
        self.assertEqual(gpus[0].pci_slot, "0000:00:02.0")
        self.assertEqual(gpus[0].vendor, "Intel")
        self.assertFalse(gpus[0].is_nvidia)

    @mock.patch("linta_nvidia._run")
    def test_detect_gpus_hybrid(self, mock_run):
        def run_side_effect(cmd, check=True):
            if cmd == ["lspci", "-nn", "-D"]:
                return _make_proc(LSPCI_HYBRID)
            if cmd[:3] == ["lspci", "-k", "-s"]:
                slot = cmd[3]
                driver = "nvidia" if "01:00.0" in slot else "i915"
                return _make_proc(f"	Kernel driver in use: {driver}\n")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        gpus = detect_gpus()
        self.assertEqual(len(gpus), 2)
        nvidia = next(g for g in gpus if g.is_nvidia)
        intel = next(g for g in gpus if not g.is_nvidia)
        self.assertEqual(nvidia.model, "NVIDIA Corporation GA106M [GeForce RTX 3060 Mobile]")
        self.assertEqual(intel.model, "Intel Corporation TigerLake-H GT1 [UHD Graphics]")
        self.assertEqual(intel.vendor, "Intel")


# --- Test 6: get_nvidia_driver_version from nvidia-smi mock ---
class TestGetNvidiaDriverVersion(unittest.TestCase):
    @mock.patch("linta_nvidia._run")
    def test_get_nvidia_driver_version_from_nvidia_smi(self, mock_run):
        mock_run.return_value = _make_proc("535.129.03\n")

        version = get_nvidia_driver_version()
        self.assertEqual(version, "535.129.03")
        mock_run.assert_called_once_with(
            [
                "nvidia-smi",
                "--query-gpu=driver_version",
                "--format=csv,noheader",
            ],
            check=False,
        )



# --- Test 7: _get_profile reads from file ---
class TestGetProfile(unittest.TestCase):
    def test_get_profile_no_file(self):
        mock_release = mock.MagicMock(spec=Path)
        mock_release.exists.return_value = False
        with mock.patch("linta_nvidia.RELEASE_FILE", mock_release):
            profile = _get_profile()
        self.assertEqual(profile, "unknown")

    def test_get_profile_reads_variant_id(self):
        mock_release = mock.MagicMock(spec=Path)
        mock_release.exists.return_value = True
        mock_release.read_text.return_value = 'VARIANT_ID="niri"\nOTHER=stuff\n'
        with mock.patch("linta_nvidia.RELEASE_FILE", mock_release):
            profile = _get_profile()
        self.assertEqual(profile, "niri")


# --- Test 8: build_parser has correct subcommands ---
class TestBuildParser(unittest.TestCase):
    def test_build_parser_has_subcommands(self):
        parser = build_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.prog, "linta-nvidia")

        subparsers_action = [a for a in parser._actions if hasattr(a, "choices") and a.choices]
        self.assertEqual(len(subparsers_action), 1)
        choices = subparsers_action[0].choices
        self.assertIn("status", choices)
        self.assertIn("setup", choices)
        self.assertIn("uninstall", choices)

    def test_build_parser_status_has_json_flag(self):
        parser = build_parser()
        args = parser.parse_args(["status", "--json"])
        self.assertEqual(args.command, "status")
        self.assertTrue(args.json)


# --- Extra: _determine_driver_branch ---
class TestDetermineDriverBranch(unittest.TestCase):
    def test_determine_driver_branch_returns_empty(self):
        gpus = [
            GpuInfo("0000:01:00.0", "NVIDIA", "RTX 3060", "nvidia", "10de:2520", True),
        ]
        branch = _determine_driver_branch(gpus)
        self.assertEqual(branch, "")


class TestEnableRpmFusion(unittest.TestCase):
    @mock.patch("linta_nvidia._run")
    def test_enable_rpm_fusion_uses_expanded_release_urls(self, mock_run):
        calls = []

        def run_side_effect(cmd, check=True):
            calls.append(cmd)
            if cmd[:2] == ["rpm", "-qa"]:
                return _make_proc("")
            if cmd == ["rpm", "-E", "%fedora"]:
                return _make_proc("42\n")
            if cmd[:3] == ["dnf", "install", "-y"]:
                return _make_proc("")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        linta_nvidia._enable_rpm_fusion()

        dnf_calls = [cmd for cmd in calls if cmd[:3] == ["dnf", "install", "-y"]]
        self.assertEqual(len(dnf_calls), 1)
        self.assertIn("rpmfusion-free-release-42.noarch.rpm", dnf_calls[0][3])
        self.assertIn("rpmfusion-nonfree-release-42.noarch.rpm", dnf_calls[0][4])
        self.assertNotIn("$(", dnf_calls[0][3])
        self.assertNotIn("$(", dnf_calls[0][4])


if __name__ == "__main__":
    unittest.main()
