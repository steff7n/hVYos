#!/usr/bin/env python3
"""Unit tests for linta-snapshots."""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import linta_snapshots


# snapper list --columns number,type,date,description,cleanup
SNAPPER_LIST_OUTPUT = """# | Type   | Date                 | Description | Cleanup
--+--------+----------------------+-------------+--------
1 | single | 2025-03-01 10:00:00 | manual      | number
2 | single | 2025-03-02 12:00:00 | pre-dnf     | number
3 | pre    | 2025-03-03 09:00:00 | weekly      | number
"""


class TestParseSnapperList(unittest.TestCase):
    """Tests for _parse_snapper_list()."""

    @patch("linta_snapshots._run")
    def test_parse_snapper_list_valid_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout=SNAPPER_LIST_OUTPUT)
        result = linta_snapshots._parse_snapper_list()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["number"], "1")
        self.assertEqual(result[0]["type"], "single")
        self.assertEqual(result[0]["date"], "2025-03-01 10:00:00")
        self.assertEqual(result[0]["description"], "manual")
        self.assertEqual(result[0]["cleanup"], "number")
        self.assertEqual(result[2]["number"], "3")
        self.assertEqual(result[2]["description"], "weekly")

    @patch("linta_snapshots._run")
    def test_parse_snapper_list_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(stdout="")
        result = linta_snapshots._parse_snapper_list()
        self.assertEqual(result, [])

    @patch("linta_snapshots._run")
    def test_parse_snapper_list_header_only(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="# | Type  | Pre # | Date\n--+-------+-------+------"
        )
        result = linta_snapshots._parse_snapper_list()
        self.assertEqual(result, [])

    @patch("linta_snapshots._run")
    def test_parse_snapper_list_subprocess_fails(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "snapper")
        result = linta_snapshots._parse_snapper_list()
        self.assertEqual(result, [])


class TestRequireRoot(unittest.TestCase):
    """Tests for _require_root()."""

    @patch("linta_snapshots.os.geteuid", return_value=1000)
    @patch("linta_snapshots.sys.exit")
    def test_require_root_exits_when_not_root(self, mock_exit, mock_geteuid):
        with patch("linta_snapshots.print"):
            linta_snapshots._require_root()
        mock_exit.assert_called_once_with(1)

    @patch("linta_snapshots.os.geteuid", return_value=0)
    @patch("linta_snapshots.sys.exit")
    def test_require_root_passes_when_root(self, mock_exit, mock_geteuid):
        linta_snapshots._require_root()
        mock_exit.assert_not_called()


class TestBuildParser(unittest.TestCase):
    """Tests for build_parser()."""

    def test_build_parser_has_subcommands(self):
        import argparse
        parser = linta_snapshots.build_parser()
        subparser_actions = [
            a for a in parser._actions
            if isinstance(a, argparse._SubParsersAction)
        ]
        self.assertEqual(len(subparser_actions), 1)
        expected = {"list", "create", "rollback", "grub-update", "diff"}
        self.assertEqual(set(subparser_actions[0].choices.keys()), expected)


class TestCmdList(unittest.TestCase):
    """Tests for cmd_list()."""

    @patch("linta_snapshots._parse_snapper_list")
    def test_cmd_list_with_snapshots(self, mock_parse):
        mock_parse.return_value = [
            {"number": "1", "type": "single", "date": "2025-03-01", "description": "manual"}
        ]
        args = MagicMock(json=False)
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            linta_snapshots.cmd_list(args)
            output = fake_out.getvalue()
        self.assertIn("1", output)
        self.assertIn("manual", output)
        self.assertIn("Total: 1 snapshot(s)", output)

    @patch("linta_snapshots._parse_snapper_list")
    def test_cmd_list_with_json_flag(self, mock_parse):
        snapshots = [
            {"number": "1", "type": "single", "date": "2025-03-01", "description": "manual", "cleanup": "number"}
        ]
        mock_parse.return_value = snapshots
        args = MagicMock(json=True)
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            linta_snapshots.cmd_list(args)
            output = fake_out.getvalue()
        parsed = json.loads(output)
        self.assertEqual(parsed, snapshots)


class TestCmdCreate(unittest.TestCase):
    """Tests for cmd_create()."""

    @patch("linta_snapshots._require_root")
    @patch("linta_snapshots._run")
    def test_cmd_create_calls_snapper_correctly(self, mock_run, mock_require):
        mock_run.return_value = MagicMock()
        args = MagicMock(description="my-snapshot", no_grub=True)
        linta_snapshots.cmd_create(args)
        mock_require.assert_called_once()
        expected_cmd = [
            "snapper", "-c", "root", "create",
            "--type", "single",
            "--description", "my-snapshot",
            "--cleanup-algorithm", "number",
        ]
        mock_run.assert_any_call(expected_cmd)

    @patch("linta_snapshots._require_root")
    @patch("linta_snapshots._run")
    def test_cmd_create_uses_default_description_when_missing(self, mock_run, mock_require):
        mock_run.return_value = MagicMock()
        args = MagicMock(description=None, no_grub=True)
        with patch("linta_snapshots.datetime") as mock_dt:
            mock_dt.now.return_value.strftime.return_value = "20250309-120000"
            linta_snapshots.cmd_create(args)
        call_args = mock_run.call_args_list[0][0][0]
        self.assertIn("manual-20250309-120000", call_args)


class TestUpdateGrubEntries(unittest.TestCase):
    """Tests for _update_grub_entries()."""

    @patch("linta_snapshots._parse_snapper_list")
    @patch("linta_snapshots._run")
    def test_update_grub_entries_embeds_concrete_uuid(self, mock_run, mock_parse):
        mock_parse.return_value = [
            {
                "number": "42",
                "type": "single",
                "date": "2025-03-09 12:00:00",
                "description": "manual",
                "cleanup": "number",
            }
        ]

        def run_side_effect(cmd, check=True):
            if cmd == ["findmnt", "-n", "-o", "UUID", "/"]:
                return MagicMock(stdout="1234-ABCD\n")
            if cmd[:2] == ["grub2-mkconfig", "-o"]:
                return MagicMock(stdout="")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        with tempfile.TemporaryDirectory() as tmp:
            grub_snapshot_cfg = Path(tmp) / "45_linta_snapshots"
            grub_cfg = Path(tmp) / "grub.cfg"
            with patch("linta_snapshots.GRUB_SNAPSHOT_CFG", grub_snapshot_cfg), patch(
                "linta_snapshots.GRUB_CFG", grub_cfg
            ):
                linta_snapshots._update_grub_entries()

            output = grub_snapshot_cfg.read_text()
            self.assertIn("1234-ABCD", output)
            self.assertNotIn("$btrfs_uuid", output)

    @patch("linta_snapshots._parse_snapper_list")
    @patch("linta_snapshots._get_boot_artifact_names", return_value=("vmlinuz-6.8.12", "initramfs-6.8.12.img"))
    @patch("linta_snapshots._run")
    def test_update_grub_entries_uses_snapshot_boot_artifacts(
        self, mock_run, mock_boot_names, mock_parse
    ):
        mock_parse.return_value = [
            {
                "number": "42",
                "type": "single",
                "date": "2025-03-09 12:00:00",
                "description": "manual",
                "cleanup": "number",
            }
        ]

        def run_side_effect(cmd, check=True):
            if cmd == ["findmnt", "-n", "-o", "UUID", "/"]:
                return MagicMock(stdout="1234-ABCD\n")
            if cmd[:2] == ["grub2-mkconfig", "-o"]:
                return MagicMock(stdout="")
            raise AssertionError(f"Unexpected command: {cmd}")

        mock_run.side_effect = run_side_effect

        with tempfile.TemporaryDirectory() as tmp:
            grub_snapshot_cfg = Path(tmp) / "45_linta_snapshots"
            grub_cfg = Path(tmp) / "grub.cfg"
            with patch("linta_snapshots.GRUB_SNAPSHOT_CFG", grub_snapshot_cfg), patch(
                "linta_snapshots.GRUB_CFG", grub_cfg
            ):
                linta_snapshots._update_grub_entries()

            output = grub_snapshot_cfg.read_text()
            self.assertIn("/@/.snapshots/42/snapshot/boot/vmlinuz-6.8.12", output)
            self.assertIn("/@/.snapshots/42/snapshot/boot/initramfs-6.8.12.img", output)


if __name__ == "__main__":
    unittest.main()
