# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Keep the Windows port free of Linux/Flatpak packaging leftovers."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".venv"}
FORBIDDEN_PARTS = {"build-aux", "flathub", "flatpak"}
FORBIDDEN_SUFFIXES = {".desktop", ".service", ".flatpak", ".flatpakref"}
FORBIDDEN_NAME_MARKERS = ("metainfo", "flatpak", "flathub")


def repository_files() -> list[Path]:
    files: list[Path] = []
    for directory, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            files.append(Path(directory) / filename)
    return files


def code_lines(path: Path) -> list[str]:
    """Return non-comment lines so documentation comments do not trip tests."""
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", ";")):
            lines.append(stripped)
    return lines


class WindowsScopeTests(unittest.TestCase):
    def test_no_linux_or_flatpak_files_are_present(self) -> None:
        for path in repository_files():
            relative = path.relative_to(ROOT)
            lower_parts = {part.lower() for part in relative.parts}
            with self.subTest(path=relative.as_posix()):
                self.assertFalse(lower_parts & FORBIDDEN_PARTS)
                self.assertNotIn(path.suffix.lower(), FORBIDDEN_SUFFIXES)
                self.assertFalse(
                    any(marker in path.name.lower() for marker in FORBIDDEN_NAME_MARKERS)
                )

    def test_build_files_do_not_install_linux_desktop_integration(self) -> None:
        forbidden = {
            "desktop_file",
            "desktop-file-validate",
            "metainfo",
            "appstream-util",
            "update-desktop-database",
            "dbusdir",
            ".service.in",
            ".desktop.in",
        }
        for relative in ("meson.build", "data/meson.build"):
            code = "\n".join(code_lines(ROOT / relative))
            for token in forbidden:
                with self.subTest(file=relative, token=token):
                    self.assertNotIn(token, code)

    def test_build_scripts_do_not_require_linux_packaging_tools(self) -> None:
        forbidden = ("appstream", "desktop-file-utils", "share/gettext/its")
        paths = (
            ROOT / "scripts" / "build-windows.sh",
            ROOT / ".github" / "workflows" / "release.yml",
        )
        for path in paths:
            code = "\n".join(code_lines(path))
            for token in forbidden:
                with self.subTest(file=path.name, token=token):
                    self.assertNotIn(token, code)

    def test_potfiles_do_not_reference_linux_entries(self) -> None:
        potfiles = (ROOT / "po" / "POTFILES").read_text(encoding="utf-8")
        self.assertNotIn(".desktop", potfiles)
        self.assertNotIn(".service", potfiles)
        self.assertNotIn("builddir", potfiles)

    def test_entrypoint_has_no_flatpak_branch(self) -> None:
        entrypoint = (ROOT / "src" / "metadata-cleaner.in").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("flatpak", entrypoint.lower())
        self.assertNotIn("setup_mimetypes", entrypoint)


if __name__ == "__main__":
    unittest.main()
