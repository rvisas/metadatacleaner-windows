# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Unit tests for the upstream-derived port version."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import versioning  # noqa: E402


class VersioningTests(unittest.TestCase):
    def test_current_version_is_composed_from_the_json_source(self) -> None:
        data = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
        upstream = data["upstream"]
        port = data["port"]
        self.assertEqual(
            versioning.compose_version(upstream, port),
            versioning.current_version(),
        )
        self.assertEqual(versioning.check_project(), versioning.current_version())

    def test_new_upstream_resets_the_port_revision_to_one(self) -> None:
        self.assertEqual(
            versioning.next_for_upstream("4.1.0"), "4.1.0.1"
        )
        self.assertEqual(
            versioning.next_for_upstream("5.0.0"), "5.0.0.1"
        )

    def test_upstream_must_have_exactly_three_components(self) -> None:
        with self.assertRaises(ValueError):
            versioning.compose_version("4.1.0.1", 1)
        with self.assertRaises(ValueError):
            versioning.compose_version("4.1", 1)

    def test_port_revision_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            versioning.compose_version("4.0.1", 0)
        with self.assertRaises(ValueError):
            versioning.compose_version("4.0.1", -1)


if __name__ == "__main__":
    unittest.main()
