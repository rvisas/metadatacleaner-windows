# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""The application name is a proper noun and must never be translated."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "po" / "es.po"
APP_NAME = "Metadata Cleaner"


class ProductNameTests(unittest.TestCase):
    def test_spanish_catalog_keeps_the_product_name(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        entry = re.search(
            r'^msgid "Metadata Cleaner"\nmsgstr "([^"]*)"$',
            catalog,
            re.MULTILINE,
        )
        self.assertIsNotNone(entry, "missing the Metadata Cleaner msgid")
        assert entry is not None
        self.assertEqual(entry.group(1), APP_NAME)

    def test_no_translated_variant_of_the_name_remains(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertNotIn("Limpiador de metadatos", catalog)
        self.assertNotIn("Limpiador de _metadatos", catalog)
        self.assertNotIn("Limpiador", catalog)

    def test_application_uses_the_name_as_a_translatable_label(self) -> None:
        app = (ROOT / "src" / "app.py").read_text(encoding="utf-8")
        self.assertIn('self.name = _("Metadata Cleaner")', app)

    def test_window_title_uses_the_untranslated_name(self) -> None:
        window = (ROOT / "data" / "ui" / "Window.ui").read_text(
            encoding="utf-8"
        )
        self.assertRegex(
            window,
            r'<property name="title" translatable="yes">Metadata Cleaner</property>',
        )

    def test_about_menu_is_translated_with_the_untranslated_name(self) -> None:
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertIn(
            'msgid "_About Metadata Cleaner"\n'
            'msgstr "Acerca de _Metadata Cleaner"',
            catalog,
        )

    def test_installer_uses_the_name_in_spanish(self) -> None:
        installer = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "spanish.UpgradeWelcome=El instalador actualizará Metadata Cleaner",
            installer,
        )


if __name__ == "__main__":
    unittest.main()
