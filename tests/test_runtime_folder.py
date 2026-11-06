# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Runtime smoke test for importing a folder from the built payload.

Set MC_PAYLOAD_DIR to the directory that contains ``MetadataCleaner.exe`` and
``share/metadata-cleaner``.  The release workflow runs this after building the
payload; a normal unit-test run skips it.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

PAYLOAD = os.environ.get("MC_PAYLOAD_DIR")


@unittest.skipUnless(PAYLOAD, "MC_PAYLOAD_DIR is not set")
class FolderImportRuntimeTests(unittest.TestCase):
    def test_folder_and_subfolder_files_are_found(self) -> None:
        self.assertIsNotNone(PAYLOAD)
        payload = Path(PAYLOAD)  # type: ignore[arg-type]
        package = payload / "share" / "metadata-cleaner"
        self.assertTrue(package.is_dir(), package)
        sys.path.insert(1, str(package))

        from gi.repository import Gio
        from metadatacleaner.modules.filestore import FileStore

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "sub").mkdir()
            (root / "one.jpg").write_bytes(b"not a real image")
            (root / "sub" / "two.pdf").write_bytes(b"not a real pdf")
            (root / "note.txt").write_bytes(b"text")

            store = FileStore()
            gfiles = store._gather_all_gfiles(
                [Gio.File.new_for_path(str(root))], True
            )

        names = sorted(gfile.get_basename() for gfile in gfiles)
        self.assertEqual(names, ["note.txt", "one.jpg", "two.pdf"])


if __name__ == "__main__":
    unittest.main()
