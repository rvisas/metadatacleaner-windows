# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guardrails for the Windows-specific changes.

These tests do not need GTK. They fail loudly when a rebase or a manual edit
drops one of the assumptions the port depends on.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WindowsPortGuardTests(unittest.TestCase):
    def test_entrypoint_is_relocatable(self) -> None:
        source = (ROOT / "src" / "metadata-cleaner.in").read_text(
            encoding="utf-8"
        )
        self.assertIn("_APP_ROOT = Path(__file__).resolve().parent.parent", source)
        self.assertIn('LOCALE_DIR = str(_APP_ROOT / "share" / "locale")', source)
        self.assertIn(
            'PKGDATA_DIR = str(_APP_ROOT / "share" / "metadata-cleaner")',
            source,
        )
        self.assertNotIn("@pkgdatadir@", source)
        self.assertNotIn("@localedir@", source)

    def test_home_directory_check_is_not_a_regex(self) -> None:
        source = (ROOT / "src" / "modules" / "file.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "dir_path.startswith(GLib.get_home_dir())", source
        )
        self.assertNotIn("re.match(GLib.get_home_dir()", source)

    def test_document_portal_xattr_is_guarded_on_windows(self) -> None:
        source = (ROOT / "src" / "modules" / "file.py").read_text(
            encoding="utf-8"
        )
        guard = 'if os.name == "nt":'
        self.assertIn(guard, source)
        guard_position = source.index(guard)
        xattr_position = source.index("xattr::document-portal.host-path")
        self.assertLess(guard_position, xattr_position)

    def test_mat2_patches_are_present(self) -> None:
        archive = (ROOT / "patches" / "0002-mat2-windows.patch").read_text(
            encoding="utf-8"
        )
        self.assertIn("stat.S_IRUSR | stat.S_IWUSR", archive)
        self.assertIn("os.replace(", archive)
        pdf = archive
        self.assertIn("as_uri()", pdf)

    def test_taskbar_identity_is_configured(self) -> None:
        entrypoint = (ROOT / "src" / "metadata-cleaner.in").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "SetCurrentProcessExplicitAppUserModelID(APP_ID)", entrypoint
        )
        self.assertIn("Gtk.Window.set_default_icon_name(APP_ID)", entrypoint)

        installer = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            '#define AppUserModelID "io.gitlab.metadatacleaner.metadatacleaner"',
            installer,
        )
        self.assertIn("AppUserModelID: \"{#AppUserModelID}\"", installer)
        self.assertIn(
            'IconFilename: "{app}\\{#AppExeName}"', installer
        )

    def test_installer_languages_are_english_and_spanish(self) -> None:
        script = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        section = script.split("[Languages]", 1)[1].split("[", 1)[0]
        languages = re.findall(r'Name:\s+"([^"]+)"', section)
        self.assertEqual(languages, ["english", "spanish"])

    def test_installer_upgrades_in_place(self) -> None:
        script = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("UsePreviousAppDir=yes", script)
        self.assertIn("UsePreviousGroup=yes", script)
        self.assertIn("GetPreviousVersion", script)
        self.assertIn("UpgradeWelcome", script)

    def test_build_outputs_stay_outside_the_repository(self) -> None:
        script = (ROOT / "scripts" / "build-windows.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("BUILD_ROOT=", script)
        self.assertIn("${TMPDIR:-/tmp}", script)
        self.assertNotIn("$ROOT/dist", script)
        installer = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("#ifndef PayloadDir", installer)
        self.assertIn("#ifndef OutputDir", installer)
        self.assertIn("OutputDir={#OutputDir}", installer)

    def test_installer_asset_name_matches_release_helper(self) -> None:
        script = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("#ifndef AppVersion", script)
        self.assertIn(
            "OutputBaseFilename=MetadataCleaner-{#AppVersion}-windows-x64-setup",
            script,
        )

    def test_installer_inputs_exist(self) -> None:
        script = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("#ifndef PayloadDir", script)
        self.assertIn('"{#PayloadDir}\\*"', script)
        icon = ROOT / "installer" / "branding" / "metadatacleaner-windows.ico"
        self.assertTrue(icon.is_file(), f"missing installer icon: {icon}")
        launcher = ROOT / "installer" / "launcher" / "MetadataCleaner.c"
        self.assertTrue(launcher.is_file(), f"missing launcher: {launcher}")

    def test_dist_is_not_versioned(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("dist", [line.strip() for line in ignore])


if __name__ == "__main__":
    unittest.main()
