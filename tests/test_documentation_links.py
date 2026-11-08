# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Documentation link and anchor checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_docs  # noqa: E402


class DocumentationLinkTests(unittest.TestCase):
    def test_all_relative_links_and_anchors_resolve(self) -> None:
        errors = check_docs.check_documentation()
        self.assertEqual(errors, [], "\n".join(errors))

    def test_readme_documentation_anchor_is_stable(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Documentation", readme)
        self.assertIn(
            "https://github.com/rvisas/metadatacleaner-windows#documentation",
            (ROOT / "src" / "ui" / "window.py").read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
