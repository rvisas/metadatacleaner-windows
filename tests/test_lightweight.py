# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guardrails for the lightweight cleaning switch."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LightweightCleaningTests(unittest.TestCase):
    def test_setting_reaches_the_mat2_parser(self) -> None:
        file_source = (ROOT / "src" / "modules" / "file.py").read_text(
            encoding="utf-8"
        )
        store_source = (ROOT / "src" / "modules" / "filestore.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "self._parser.lightweight_cleaning = lightweight_mode",
            file_source,
        )
        self.assertIn(
            "self.clean_files_executor.submit(f.clean, self.lightweight_mode)",
            store_source,
        )

    def test_switch_is_visible_and_translatable(self) -> None:
        ui = (ROOT / "data" / "ui" / "SettingsButton.ui").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            '<property name="title" translatable="yes">Lightweight Cleaning</property>',
            ui,
        )
        self.assertIn(
            '<property name="subtitle" translatable="yes">',
            ui,
        )


if __name__ == "__main__":
    unittest.main()
