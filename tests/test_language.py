# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Language selection tests: English and Spanish only."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from modules import language  # noqa: E402


class NormalizeTests(unittest.TestCase):
    def test_spanish_variants(self) -> None:
        for value in (
            "es",
            "es_ES",
            "es-MX",
            "Spanish",
            "spa",
            "es_ES.UTF-8",
            "es_PE",
        ):
            self.assertEqual(language.normalize_language(value), "es", value)

    def test_english_variants(self) -> None:
        for value in ("en", "en_US", "en-GB", "English", "eng", "en_US.UTF-8"):
            self.assertEqual(language.normalize_language(value), "en", value)

    def test_unsupported_languages_are_rejected(self) -> None:
        for value in ("fr", "de", "pt_BR", "zh_CN", "", None):
            self.assertIsNone(language.normalize_language(value), value)


class ResolveTests(unittest.TestCase):
    def test_only_english_and_spanish_are_supported(self) -> None:
        self.assertEqual(language.SUPPORTED, ("en", "es"))

    def test_explicit_override_wins(self) -> None:
        self.assertEqual(
            language.resolve_language(
                explicit="es", installer="en", environment="en_US", system="en"
            ),
            "es",
        )

    def test_installer_choice_beats_the_environment(self) -> None:
        self.assertEqual(
            language.resolve_language(
                installer="es", environment="en_US", system="en"
            ),
            "es",
        )

    def test_environment_is_used_without_an_installer_value(self) -> None:
        self.assertEqual(
            language.resolve_language(environment="es_MX.UTF-8", system="en"),
            "es",
        )

    def test_system_language_is_the_last_fallback(self) -> None:
        self.assertEqual(language.resolve_language(system="es_ES"), "es")

    def test_unsupported_values_fall_back_to_english(self) -> None:
        self.assertEqual(
            language.resolve_language(
                explicit="fr", installer="de", environment="pt_BR", system="it"
            ),
            "en",
        )

    def test_apply_language_sets_gettext_variables(self) -> None:
        import os

        previous = {
            key: os.environ.get(key)
            for key in ("LANG", "LANGUAGE", "LC_ALL", "LC_MESSAGES")
        }
        try:
            language.apply_language("es")
            self.assertEqual(os.environ["LANGUAGE"], "es")
            self.assertTrue(os.environ["LANG"].startswith("es"))
            language.apply_language("en")
            self.assertEqual(os.environ["LANGUAGE"], "en")
            self.assertTrue(os.environ["LANG"].startswith("en"))
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class EntrypointTests(unittest.TestCase):
    def test_entrypoint_binds_the_c_gettext_domain(self) -> None:
        source = (ROOT / "src" / "metadata-cleaner.in").read_text(
            encoding="utf-8"
        )
        self.assertIn("detect_language()", source)
        self.assertIn("apply_language(language)", source)
        self.assertIn("_bind_libintl()", source)
        self.assertIn("libintl_bindtextdomain", source)
        self.assertIn("libintl_textdomain", source)

    def test_installer_writes_the_chosen_language(self) -> None:
        installer = (ROOT / "installer" / "metadatacleaner.iss").read_text(
            encoding="utf-8"
        )
        self.assertIn("ActiveLanguage", installer)
        self.assertIn("Software\\Metadata Cleaner", installer)


if __name__ == "__main__":
    unittest.main()
