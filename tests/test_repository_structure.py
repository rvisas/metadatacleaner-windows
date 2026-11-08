# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guardrails for the repository layout used by contributors and AI agents."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "AGENTS.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "docs/architecture.md",
    "docs/build.md",
    "docs/code-signing.md",
    "docs/releasing.md",
    "docs/upstream.md",
    "docs/versioning.md",
    ".github/workflows/release.yml",
    ".github/workflows/tests.yml",
    "installer/metadatacleaner.iss",
    "scripts/build-windows.sh",
    "version.json",
}


def repository_files() -> list[str]:
    """List files without requiring git to be installed in the CI shell."""
    files: list[str] = []
    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in {".git", "__pycache__", ".venv"}
        ]
        for filename in filenames:
            path = Path(directory) / filename
            files.append(path.relative_to(ROOT).as_posix())
    return files


class RepositoryStructureTests(unittest.TestCase):
    def test_required_project_files_exist(self) -> None:
        for relative in sorted(REQUIRED):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_documentation_topics_are_english_and_lowercase(self) -> None:
        for path in (ROOT / "docs").iterdir():
            if path.is_file():
                with self.subTest(path=path.name):
                    self.assertEqual(path.name, path.name.lower())

    def test_tracked_paths_are_ascii(self) -> None:
        for relative in repository_files():
            with self.subTest(path=relative):
                relative.encode("ascii")

    def test_obsolete_layout_is_not_tracked(self) -> None:
        obsolete_paths = {
            "UPSTREAM.md",
            "docs/BUILD.md",
            "docs/RELEASING.md",
            "docs/SIGNPATH.md",
            "Makefile",
        }
        obsolete_parts = {"build-aux", "dist", "__pycache__"}
        for relative in repository_files():
            with self.subTest(path=relative):
                self.assertNotIn(relative, obsolete_paths)
                self.assertFalse(
                    set(Path(relative).parts) & obsolete_parts, relative
                )
                self.assertNotIn(
                    Path(relative).suffix.lower(), {".exe", ".msi", ".mo"}
                )

    def test_versioning_document_matches_current_release(self) -> None:
        text = (ROOT / "docs" / "versioning.md").read_text(encoding="utf-8")
        meson = (ROOT / "meson.build").read_text(encoding="utf-8")
        self.assertIn("4.0.1.4", text)
        self.assertIn("version: '4.0.1.4'", meson)


if __name__ == "__main__":
    unittest.main()
