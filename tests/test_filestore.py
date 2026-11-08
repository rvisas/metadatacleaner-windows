# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Regression tests for folder imports.

The folder picker used to hand FileStore a directory, but the GIO enumerator
was asked for no attributes at all.  In that case every child has
G_FILE_TYPE_UNKNOWN and the import silently adds zero files.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILESTORE = ROOT / "src" / "modules" / "filestore.py"


class FolderImportTests(unittest.TestCase):
    def test_enumerator_requests_type_and_name(self) -> None:
        source = FILESTORE.read_text(encoding="utf-8")
        self.assertIn(
            '_DIRECTORY_ATTRIBUTES = "standard::name,standard::type"',
            source,
        )
        self.assertIn(
            "self._DIRECTORY_ATTRIBUTES", source
        )
        # An empty attribute list is the original bug: GFileInfo then has
        # no standard::type, so _get_gfiles_from_dir skips every child.
        self.assertNotIn('enumerate_children(\n            ""', source)

    def test_empty_folder_does_not_leave_the_store_working(self) -> None:
        source = FILESTORE.read_text(encoding="utf-8")
        self.assertIn("if not futures:\n                return", source)
        self.assertIn("finally:\n            self._stop_adding_gfiles()", source)

    def test_folder_walk_is_iterative_and_not_nested(self) -> None:
        source = FILESTORE.read_text(encoding="utf-8")
        # A new pool per directory was the old behavior: it creates one thread
        # per directory and defeats the shared add pool.
        self.assertNotIn("with ThreadPoolExecutor() as executor", source)
        self.assertIn("def _iter_gfiles_from_dir", source)
        self.assertIn("pending = [dir]", source)

    def test_known_paths_index_replaces_linear_duplicate_scan(self) -> None:
        source = FILESTORE.read_text(encoding="utf-8")
        self.assertIn("self._known_paths", source)
        self.assertNotIn(
            "bool(list(filter(lambda x: x.path == gfile.get_path(), self)))",
            source,
        )


if __name__ == "__main__":
    unittest.main()
