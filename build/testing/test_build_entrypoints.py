#!/usr/bin/env python3
"""Regression tests for build and test entrypoints."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


class TestRunTestsScript(unittest.TestCase):
    """Tests for scripts/run-tests.sh."""

    def test_run_tests_executes_all_slots_and_summarizes(self) -> None:
        script_path = REPO_ROOT / "scripts" / "run-tests.sh"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copied_script = tmp_root / "scripts" / "run-tests.sh"
            copied_script.parent.mkdir(parents=True, exist_ok=True)
            copied_script.write_text(script_path.read_text())
            copied_script.chmod(copied_script.stat().st_mode | stat.S_IEXEC)

            testing_dir = tmp_root / "build" / "testing"
            testing_dir.mkdir(parents=True, exist_ok=True)
            _write_executable(
                testing_dir / "validate-manifests.sh",
                "#!/bin/sh\n"
                "echo manifest-ok\n"
                "exit 0\n",
            )
            _write_executable(
                testing_dir / "validate-kickstarts.sh",
                "#!/bin/sh\n"
                "echo kickstart-ok\n"
                "exit 0\n",
            )

            result = subprocess.run(
                ["bash", str(copied_script)],
                cwd=tmp_root,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("[1] Package manifest validation", result.stdout)
            self.assertIn("[2] Kickstart file validation", result.stdout)
            self.assertIn("Results: 2/2 passed, 0 failed", result.stdout)


class TestContainerEntrypoint(unittest.TestCase):
    """Tests for build/container-entry.sh."""

    def test_container_test_runs_full_suite_and_succeeds(self) -> None:
        script_path = REPO_ROOT / "build" / "container-entry.sh"
        expected_suites = {
            "packages/lintactl": ["test_lintactl.py"],
            "packages/linta-snapshots": ["test_linta_snapshots.py"],
            "packages/linta-nvidia": ["test_linta_nvidia.py"],
            "packages/linta-welcome": ["test_linta_welcome.py"],
            "packages/linta-flatpak-manager": ["test_linta_flatpak_manager.py"],
            "packages/linta-keybindings": ["test_linta_keybindings.py"],
            "installer": ["test_linta_installer.py"],
            "build/testing": [
                "test_build_with_container.py",
                "test_build_entrypoints.py",
                "test_runtime_configs.py",
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            script_copy = tmp_root / "container-entry.sh"
            script_copy.write_text(
                script_path.read_text().replace('WORKSPACE="/workspace"', f'WORKSPACE="{tmp_root}"')
            )
            script_copy.chmod(script_copy.stat().st_mode | stat.S_IEXEC)

            command_log = tmp_root / "python3.log"
            bin_dir = tmp_root / "bin"
            bin_dir.mkdir()
            _write_executable(
                bin_dir / "python3",
                "#!/bin/sh\n"
                f"printf '%s|%s\\n' \"$PWD\" \"$*\" >> \"{command_log}\"\n"
                "exit 0\n",
            )

            for rel_dir, test_files in expected_suites.items():
                test_dir = tmp_root / rel_dir
                test_dir.mkdir(parents=True, exist_ok=True)
                for test_file in test_files:
                    (test_dir / test_file).write_text("def test_placeholder():\n    pass\n")

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:{env['PATH']}"

            result = subprocess.run(
                ["bash", str(script_copy), "test"],
                cwd=tmp_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Results: 8/8 test suites passed", result.stdout)

            logged_commands = {}
            for line in command_log.read_text().splitlines():
                cwd, args = line.split("|", 1)
                logged_commands[str(Path(cwd).relative_to(tmp_root))] = args

            self.assertEqual(set(logged_commands), set(expected_suites))
            self.assertIn("test_lintactl.py", logged_commands["packages/lintactl"])
            self.assertIn("test_linta_installer.py", logged_commands["installer"])
            self.assertIn("test_build_with_container.py", logged_commands["build/testing"])
            self.assertIn("test_build_entrypoints.py", logged_commands["build/testing"])
            self.assertIn("test_runtime_configs.py", logged_commands["build/testing"])


class TestBuildConfigRegressions(unittest.TestCase):
    """Tests for build configuration consistency."""

    def test_mock_config_uses_mirrorlist_for_mirrorlist_endpoints(self) -> None:
        config = (REPO_ROOT / "build" / "mock" / "linta-fc42-x86_64.cfg").read_text()

        self.assertIn("mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-42&arch=$basearch", config)
        self.assertIn(
            "mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f42&arch=$basearch",
            config,
        )
        self.assertNotIn(
            "baseurl=https://mirrors.fedoraproject.org/mirrorlist?repo=fedora-42&arch=$basearch",
            config,
        )

    def test_container_and_standalone_iso_builders_are_aligned(self) -> None:
        container_entry = (REPO_ROOT / "build" / "container-entry.sh").read_text()
        standalone_script = (REPO_ROOT / "scripts" / "build-iso.sh").read_text()

        self.assertIn("livemedia-creator", container_entry)
        self.assertNotIn("livecd-creator", container_entry)
        self.assertIn("livemedia-creator", standalone_script)

    def test_makefile_runs_all_build_testing_regressions(self) -> None:
        makefile = (REPO_ROOT / "Makefile").read_text()

        self.assertIn("test_build_with_container.py", makefile)
        self.assertIn("test_build_entrypoints.py", makefile)
        self.assertIn("test_runtime_configs.py", makefile)


class TestValidationScripts(unittest.TestCase):
    """Tests for build/testing validation scripts."""

    def test_validate_manifests_reports_repoquery_failure(self) -> None:
        script_path = REPO_ROOT / "build" / "testing" / "validate-manifests.sh"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            copied_script = tmp_root / "build" / "testing" / "validate-manifests.sh"
            copied_script.parent.mkdir(parents=True, exist_ok=True)
            copied_script.write_text(script_path.read_text())
            copied_script.chmod(copied_script.stat().st_mode | stat.S_IEXEC)

            packages_dir = tmp_root / "build" / "packages"
            specs_dir = packages_dir / "specs"
            specs_dir.mkdir(parents=True, exist_ok=True)
            (packages_dir / "base.txt").write_text("bash\n")

            bin_dir = tmp_root / "bin"
            bin_dir.mkdir()
            _write_executable(
                bin_dir / "dnf",
                "#!/bin/sh\n"
                "exit 42\n",
            )

            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}:{env['PATH']}"

            result = subprocess.run(
                ["bash", str(copied_script)],
                cwd=tmp_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error: dnf repoquery failed.", result.stdout)
            self.assertNotIn("FAIL: bash", result.stdout)

    def test_validate_kickstarts_passes_explicit_version_to_ksflatten(self) -> None:
        """Regress: validate-kickstarts.sh must pass explicit Fedora version to ksflatten."""
        script_path = REPO_ROOT / "build" / "testing" / "validate-kickstarts.sh"
        source = script_path.read_text()
        self.assertIn("RELEASEVER", source)
        self.assertIn("--version", source)
        self.assertIn("ksflatten", source)
        # Must call ksflatten with --version F${RELEASEVER}
        self.assertIn('"F${RELEASEVER}"', source)


if __name__ == "__main__":
    unittest.main()
