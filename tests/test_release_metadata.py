# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for release naming and checksum helpers."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release_metadata  # noqa: E402


class ReleaseMetadataTests(unittest.TestCase):
    def test_installer_name_encodes_port_os_and_arch(self) -> None:
        self.assertEqual(
            release_metadata.installer_filename("4.0.1"),
            "MetadataCleaner-4.0.1-windows-x64-setup.exe",
        )

    def test_checksum_sidecar_name(self) -> None:
        name = release_metadata.installer_filename("4.0.1")
        self.assertEqual(
            release_metadata.checksum_filename(name),
            "MetadataCleaner-4.0.1-windows-x64-setup.exe.sha256",
        )

    def test_port_specific_tag_does_not_collide_with_upstream(self) -> None:
        self.assertEqual(
            release_metadata.release_tag("4.0.1"), "v4.0.1-windows.1"
        )
        self.assertEqual(
            release_metadata.release_tag("4.0.1", 2), "v4.0.1-windows.2"
        )
        with self.assertRaises(ValueError):
            release_metadata.release_tag("4.0.1", 0)

    def test_sha256_and_checksum_line(self) -> None:
        payload = b"metadata-cleaner\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset.exe"
            path.write_bytes(payload)
            expected = hashlib.sha256(payload).hexdigest()
            self.assertEqual(release_metadata.sha256_file(path), expected)
            self.assertEqual(
                release_metadata.checksum_line(path),
                f"{expected}  asset.exe",
            )


if __name__ == "__main__":
    unittest.main()
