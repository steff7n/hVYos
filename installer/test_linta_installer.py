#!/usr/bin/env python3
"""Unit tests for the Linta installer."""

from __future__ import annotations

import unittest

import linta_installer


class TestPartitionDevice(unittest.TestCase):
    """Tests for partition device path derivation."""

    def test_partition_device_handles_nvme_and_sata_names(self) -> None:
        self.assertEqual(
            linta_installer._partition_device("/dev/nvme0n1", 1),
            "/dev/nvme0n1p1",
        )
        self.assertEqual(
            linta_installer._partition_device("/dev/nvme0n1", 3),
            "/dev/nvme0n1p3",
        )
        self.assertEqual(
            linta_installer._partition_device("/dev/sda", 2),
            "/dev/sda2",
        )


if __name__ == "__main__":
    unittest.main()
