#!/usr/bin/env python3
"""Tests for scripts/build-with-container.sh."""

from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


class TestBuildWithContainerScript(unittest.TestCase):
    """Tests runtime-specific image existence checks."""

    def test_docker_runtime_uses_docker_supported_image_check(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        script_path = repo_root / "scripts" / "build-with-container.sh"

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            command_log = tmpdir / "docker.log"
            docker = tmpdir / "docker"
            docker.write_text(
                "#!/bin/sh\n"
                f"printf '%s\\n' \"$*\" >> \"{command_log}\"\n"
                "if [ \"$1\" = image ] && [ \"$2\" = inspect ]; then\n"
                "  exit 1\n"
                "fi\n"
                "if [ \"$1\" = image ] && [ \"$2\" = exists ]; then\n"
                "  echo \"docker: 'exists' is not a docker command.\" >&2\n"
                "  exit 125\n"
                "fi\n"
                "exit 0\n"
            )
            docker.chmod(docker.stat().st_mode | stat.S_IEXEC)

            env = os.environ.copy()
            env["PATH"] = f"{tmp}:{env['PATH']}"
            env["LINTA_CONTAINER_RUNTIME"] = "docker"

            result = subprocess.run(
                ["bash", str(script_path), "help"],
                cwd=repo_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            commands = command_log.read_text().splitlines()
            self.assertIn("image inspect linta-builder", commands)
            self.assertNotIn("image exists linta-builder", commands)


if __name__ == "__main__":
    unittest.main()
