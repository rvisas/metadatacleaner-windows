# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Runtime test for the thorough and lightweight cleaning paths."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PAYLOAD = os.environ.get("MC_PAYLOAD_DIR")
FIXTURE = Path(__file__).resolve().parent / "data" / "with_metadata.jpg"


@unittest.skipUnless(PAYLOAD, "MC_PAYLOAD_DIR is not set")
class LightweightRuntimeTests(unittest.TestCase):
    def test_both_modes_clean_a_jpeg(self) -> None:
        self.assertIsNotNone(PAYLOAD)
        payload = Path(PAYLOAD)  # type: ignore[arg-type]
        package = payload / "share" / "metadata-cleaner"
        self.assertTrue(package.is_dir(), package)
        sys.path.insert(1, str(package))

        from gi.repository import Gio
        from metadatacleaner.modules.file import File, FileState

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, lightweight in (
                ("thorough.jpg", False),
                ("lightweight.jpg", True),
            ):
                target = root / name
                shutil.copyfile(FIXTURE, target)
                file = File(Gio.File.new_for_path(str(target)))
                file.check_metadata()
                self.assertEqual(file.state, FileState.HAS_METADATA)
                file.clean(lightweight_mode=lightweight)
                self.assertEqual(file.state, FileState.CLEANED)
                self.assertIsNone(file.error)
                self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main()
