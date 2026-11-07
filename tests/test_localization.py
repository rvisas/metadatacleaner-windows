# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Localization guardrails for the Windows build."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
PO = ROOT / "po" / "es.po"


def _string(lines: list[str], prefix: str) -> str:
    """Read a possibly-multiline PO string."""
    values: list[str] = []
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        part = line[len(prefix):].strip()
        if not part.startswith('"'):
            return ""
        values.append(part[1:-1])
        for continuation in lines[index + 1:]:
            if not continuation.startswith('"'):
                break
            values.append(continuation[1:-1])
        return "".join(values)
    return ""


def load_spanish() -> dict[str, str]:
    entries: dict[str, str] = {}
    for block in PO.read_text(encoding="utf-8").split("\n\n"):
        lines = block.splitlines()
        if not any(line.startswith("msgid ") for line in lines):
            continue
        if any(line.startswith("#~") for line in lines):
            continue
        msgid = _string(lines, "msgid ")
        if not msgid:
            continue
        if any(line.startswith("msgstr[") for line in lines):
            entries[msgid] = "\n".join(
                _string(lines, f"msgstr[{index}]") for index in range(2)
            )
        else:
            entries[msgid] = _string(lines, "msgstr ")
    return entries


class SpanishLocalizationTests(unittest.TestCase):
    def test_lightweight_explanation_is_spanish(self) -> None:
        entries = load_spanish()
        self.assertEqual(entries["Lightweight Cleaning"], "Limpieza ligera")
        subtitle = next(
            value
            for key, value in entries.items()
            if key.startswith("By default, the removal process")
        )
        self.assertTrue(subtitle.startswith("De forma predeterminada"))
        self.assertIn("modo ligero", subtitle)
        self.assertNotIn("By default", subtitle)

    def test_core_ui_strings_are_translated(self) -> None:
        entries = load_spanish()
        expected = {
            "Close Window": "Cerrar ventana",
            "Add Files": "Añadir archivos",
            "Add Folders": "Añadir carpetas",
            "Clean Metadata": "Limpiar metadatos",
            "Settings": "Ajustes",
            "Clea_r List of Files": "_Vaciar la lista de archivos",
        }
        for msgid, translation in expected.items():
            self.assertEqual(entries.get(msgid), translation, msgid)

    def test_translatable_ui_strings_have_a_translation(self) -> None:
        entries = load_spanish()
        missing = []
        for path in (ROOT / "data").rglob("*.ui"):
            root = ElementTree.parse(path).getroot()
            for element in root.iter():
                if element.get("translatable") != "yes":
                    continue
                text = (element.text or "").strip()
                if text and text not in entries:
                    missing.append((path.name, text))
        self.assertEqual(missing, [], f"untranslated UI strings: {missing}")

    def test_python_strings_have_a_translation(self) -> None:
        entries = {
            key.replace("\\n", "\n"): value
            for key, value in load_spanish().items()
        }
        missing = set()
        for path in (ROOT / "src").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not isinstance(node.func, ast.Name) or node.func.id != "_":
                    continue
                if not node.args:
                    continue
                argument = node.args[0]
                if isinstance(argument, ast.Constant) and isinstance(
                    argument.value, str
                ):
                    if argument.value and argument.value not in entries:
                        missing.add(argument.value)
        self.assertEqual(missing, set(), f"untranslated Python strings: {missing}")

    def test_no_active_translation_is_empty(self) -> None:
        entries = load_spanish()
        empty = [key for key, value in entries.items() if not value.strip()]
        self.assertEqual(empty, [], f"empty Spanish translations: {empty}")


if __name__ == "__main__":
    unittest.main()
