# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Fail loudly when an upstream update changes the port's assumptions.

The upstream is a Linux GTK application. These contract tests are intentionally
static: they can run without GTK, a payload or a display, and they identify the
files, classes, actions and settings the Windows port depends on.
"""

from __future__ import annotations

import ast
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "src/app.py",
    "src/metadata-cleaner.in",
    "src/modules/file.py",
    "src/modules/filestore.py",
    "src/modules/language.py",
    "src/modules/updater.py",
    "src/ui/window.py",
    "src/ui/settingsbutton.py",
    "data/ui/Window.ui",
    "data/io.gitlab.metadatacleaner.metadatacleaner.gschema.xml",
    "installer/metadatacleaner.iss",
    "patches/0001-app-windows.patch",
    "patches/0002-mat2-windows.patch",
    "patches/0003-windows-taskbar.patch",
    "po/POTFILES",
    "po/es.po",
)

EXPECTED_CLASSES = {
    "src/app.py": ("MetadataCleaner", {"do_activate", "check_for_updates", "_present_update"}),
    "src/ui/window.py": ("Window", {"show_toast", "_setup_file_store"}),
    "src/modules/file.py": ("File", {"check_metadata", "clean"}),
    "src/modules/filestore.py": ("FileStore", {"add_gfiles", "_get_gfiles_from_dir"}),
}

EXPECTED_FUNCTIONS = {
    "src/modules/language.py": {"resolve_language", "detect_language", "apply_language"},
    "src/modules/updater.py": {"parse_version", "pick_update", "download_update"},
    "src/metadata-cleaner.in": {"setup_i18n", "setup_resources", "run_app"},
}


def parse_python(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


class UpstreamContractTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for relative in REQUIRED:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_classes_and_methods_used_by_the_port_exist(self) -> None:
        for relative, (class_name, methods) in EXPECTED_CLASSES.items():
            tree = parse_python(ROOT / relative)
            classes = {
                node.name: node
                for node in tree.body
                if isinstance(node, ast.ClassDef)
            }
            with self.subTest(file=relative, class_name=class_name):
                self.assertIn(class_name, classes)
                members = {
                    node.name
                    for node in classes[class_name].body
                    if isinstance(node, ast.FunctionDef)
                }
                self.assertTrue(methods <= members, methods - members)

    def test_functions_used_by_the_port_exist(self) -> None:
        for relative, functions in EXPECTED_FUNCTIONS.items():
            tree = parse_python(ROOT / relative)
            names = {
                node.name
                for node in tree.body
                if isinstance(node, ast.FunctionDef)
            }
            with self.subTest(file=relative):
                self.assertTrue(functions <= names, functions - names)

    def test_window_actions_still_exist(self) -> None:
        ui = (ROOT / "data" / "ui" / "Window.ui").read_text(encoding="utf-8")
        for action in (
            "win.add-files",
            "win.add-folders",
            "win.toggle-details-view",
            "win.info",
        ):
            with self.subTest(action=action):
                self.assertIn(action, ui)

    def test_settings_used_by_python_exist_in_the_schema(self) -> None:
        schema = ET.parse(
            ROOT
            / "data"
            / "io.gitlab.metadatacleaner.metadatacleaner.gschema.xml"
        )
        declared = {
            element.get("name")
            for element in schema.getroot().iter("key")
            if element.get("name")
        }
        source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "src").rglob("*.py")
        )
        used = set(
            re.findall(
                r"\.get_(?:boolean|int64|string|int|double)\(\"([^\"]+)\"\)",
                source,
            )
        )
        self.assertTrue(used <= declared, used - declared)

    def test_potfiles_point_to_existing_files(self) -> None:
        potfiles = (ROOT / "po" / "POTFILES").read_text(encoding="utf-8")
        entries = [
            line.strip().removeprefix("./")
            for line in potfiles.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        for relative in entries:
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_potfiles_cover_translatable_ui(self) -> None:
        potfiles = (ROOT / "po" / "POTFILES").read_text(encoding="utf-8")
        for path in sorted((ROOT / "data").rglob("*.ui")):
            if 'translatable="yes"' not in path.read_text(encoding="utf-8"):
                continue
            relative = path.relative_to(ROOT).as_posix()
            with self.subTest(path=relative):
                self.assertIn(relative, potfiles)

    def test_upstream_base_is_documented(self) -> None:
        upstream = (ROOT / "docs" / "upstream.md").read_text(encoding="utf-8")
        self.assertIn("v4.0.1", upstream)
        self.assertIn("4.0.1.7", upstream)

    def test_readme_points_to_the_versioning_rules(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Versioning", readme)
        self.assertIn("derived from the upstream", readme)
        self.assertIn("docs/versioning.md", readme)
        self.assertIn("docs/upstream.md", readme)


if __name__ == "__main__":
    unittest.main()
