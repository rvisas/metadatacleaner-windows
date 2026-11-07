# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Guardrails for the automatic update check."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UpdateIntegrationTests(unittest.TestCase):
    def test_settings_are_declared(self) -> None:
        schema = (ROOT / "data" / "io.gitlab.metadatacleaner.metadatacleaner.gschema.xml").read_text(
            encoding="utf-8"
        )
        self.assertIn('name="check-for-updates" type="b"', schema)
        self.assertIn('name="last-update-check" type="x"', schema)

    def test_update_actions_are_wired(self) -> None:
        app = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
        self.assertIn('create_action("check-for-updates")', app)
        self.assertIn('SimpleAction.new("check-updates"', app)
        self.assertIn("updater.pick_update", app)
        self.assertIn("updater.download_update", app)
        settings_ui = (ROOT / "data" / "ui" / "SettingsButton.ui").read_text(
            encoding="utf-8"
        )
        menu_ui = (ROOT / "data" / "ui" / "MenuButton.ui").read_text(
            encoding="utf-8"
        )
        self.assertIn("app.check-for-updates", settings_ui)
        self.assertIn("app.check-updates", menu_ui)

    def test_update_is_available_in_the_settings_dialog(self) -> None:
        settings = (ROOT / "src" / "ui" / "settingsbutton.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("show_pref_dialog", settings)


if __name__ == "__main__":
    unittest.main()
