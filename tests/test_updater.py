# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the GitHub release updater."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules import updater  # noqa: E402


def release(
    tag: str,
    *,
    version: str | None = None,
    draft: bool = False,
    prerelease: bool = True,
    digest: bool = True,
) -> dict:
    version = version or tag.removeprefix("v").removesuffix("-windows")
    installer_name = (
        f"MetadataCleaner-{version}-windows-x64-setup.exe"
    )
    assets = [
        {
            "name": installer_name,
            "browser_download_url": (
                "https://github.com/rvisas/metadatacleaner-windows/"
                f"releases/download/{tag}/{installer_name}"
            ),
            "digest": (
                "sha256:"
                "2dd9d164775013a81b249080fef73d93fdaf7a2898c73dcad8719bbed3bca85f"
                if digest
                else ""
            ),
        }
    ]
    if not digest:
        assets.append(
            {
                "name": installer_name + ".sha256",
                "browser_download_url": (
                    "https://github.com/rvisas/metadatacleaner-windows/"
                    f"releases/download/{tag}/{installer_name}.sha256"
                ),
            }
        )
    return {
        "tag_name": tag,
        "name": tag,
        "draft": draft,
        "prerelease": prerelease,
        "body": f"Notes for {version}",
        "assets": assets,
    }


class VersionTests(unittest.TestCase):
    def test_parse_version(self) -> None:
        self.assertEqual(updater.parse_version("4.0.1"), (4, 0, 1))
        self.assertEqual(updater.parse_version(" 10.20.30 "), (10, 20, 30))
        self.assertIsNone(updater.parse_version("4.0"))
        self.assertIsNone(updater.parse_version("v4.0.1"))
        self.assertIsNone(updater.parse_version("4.0.1-beta"))

    def test_invalid_current_version_is_rejected(self) -> None:
        with self.assertRaises(updater.UpdateError):
            updater.pick_update([], "not-a-version")


class ReleaseSelectionTests(unittest.TestCase):
    def test_chooses_the_highest_newer_release(self) -> None:
        update = updater.pick_update(
            [
                release("v4.0.2-windows"),
                release("v4.1.0-windows"),
                release("v4.0.1-windows"),
            ],
            "4.0.1",
        )
        self.assertIsNotNone(update)
        self.assertEqual(update.version, "4.1.0")
        self.assertEqual(update.sha256[:7], "2dd9d16")

    def test_ignores_current_and_older_releases(self) -> None:
        self.assertIsNone(
            updater.pick_update(
                [
                    release("v4.0.1-windows"),
                    release("v4.0.0-windows"),
                ],
                "4.0.1",
            )
        )

    def test_ignores_drafts_and_unrelated_tags(self) -> None:
        self.assertIsNone(
            updater.pick_update(
                [
                    release("v4.1.0-windows", draft=True),
                    release("v4.1.0-linux"),
                ],
                "4.0.1",
            )
        )

    def test_accepts_prereleases(self) -> None:
        update = updater.pick_update(
            [release("v4.2.0-windows", prerelease=True)], "4.0.1"
        )
        self.assertIsNotNone(update)
        self.assertEqual(update.version, "4.2.0")

    def test_requires_a_matching_x64_installer(self) -> None:
        item = release("v4.1.0-windows")
        item["assets"][0]["name"] = "MetadataCleaner-4.1.0-linux-x64.tar.gz"
        self.assertIsNone(updater.pick_update([item], "4.0.1"))

    def test_accepts_sidecar_when_digest_is_missing(self) -> None:
        update = updater.pick_update(
            [release("v4.1.0-windows", digest=False)], "4.0.1"
        )
        self.assertIsNotNone(update)
        self.assertEqual(update.sha256, "")
        self.assertTrue(update.sha256_url.endswith(".sha256"))


class ChecksumTests(unittest.TestCase):
    def test_sha256_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "installer.exe"
            path.write_bytes(b"metadata-cleaner")
            expected = hashlib.sha256(b"metadata-cleaner").hexdigest()
            self.assertEqual(updater.sha256_file(path), expected)

    def test_download_accepts_a_good_checksum(self) -> None:
        payload = b"installer bytes"
        good = hashlib.sha256(payload).hexdigest()
        update = updater.Update(
            version="4.1.0",
            tag="v4.1.0-windows",
            installer_url="https://example.invalid/MetadataCleaner-4.1.0-windows-x64-setup.exe",
            sha256=good,
        )

        class Response:
            def __init__(self) -> None:
                self.data = payload
                self.sent = False

            def read(self, size: int = -1) -> bytes:
                if self.sent:
                    return b""
                self.sent = True
                return self.data

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(
                updater.urllib.request, "urlopen", return_value=Response()
            ):
                path = updater.download_update(
                    update, Path(temporary), timeout=1
                )
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(path.name, "MetadataCleaner-4.1.0-windows-x64-setup.exe")

    def test_download_rejects_bad_checksum(self) -> None:
        payload = b"not the expected installer"
        good = hashlib.sha256(payload).hexdigest()
        update = updater.Update(
            version="4.1.0",
            tag="v4.1.0-windows",
            installer_url="https://example.invalid/setup.exe",
            sha256="0" * 64,
        )

        class Response:
            def __init__(self) -> None:
                self.data = payload

            def read(self, size: int = -1) -> bytes:
                if not self.data:
                    return b""
                data, self.data = self.data, b""
                return data

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(
                updater.urllib.request, "urlopen", return_value=Response()
            ):
                with self.assertRaises(updater.UpdateError):
                    updater.download_update(
                        update, Path(temporary), timeout=1
                    )
            self.assertEqual(list(Path(temporary).glob("*.exe")), [])

        self.assertNotEqual(good, update.sha256)


class ReleasePayloadTests(unittest.TestCase):
    def test_github_payload_fixture_is_a_list(self) -> None:
        fixture = json.dumps([release("v4.1.0-windows")])
        self.assertTrue(fixture.startswith("["))
        self.assertIn("v4.1.0-windows", fixture)


if __name__ == "__main__":
    unittest.main()
