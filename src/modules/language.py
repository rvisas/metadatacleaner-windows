# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Pick the interface language for the Windows build.

The application ships English and Spanish only.  On Windows the process is
usually started by Explorer, which does not export ``LANG``; without a value
GNU gettext falls back to the C locale and the whole interface stays English
even when the setup wizard was run in Spanish.  This module decides the
language from, in order:

1. the ``MC_LANGUAGE`` environment variable (explicit override);
2. the language chosen in the installer (registry value);
3. ``LANG``/``LANGUAGE``/``LC_ALL`` inherited from the environment;
4. the Windows display language;
5. English.
"""

from __future__ import annotations

import os
import sys

SUPPORTED = ("en", "es")
DEFAULT = "en"
REGISTRY_KEY = r"Software\Metadata Cleaner"
REGISTRY_VALUE = "Language"

_ALIASES = {
    "en": "en",
    "eng": "en",
    "english": "en",
    "en_us": "en",
    "en_gb": "en",
    "es": "es",
    "spa": "es",
    "spanish": "es",
    "es_es": "es",
    "es_mx": "es",
    "es_pe": "es",
}


def normalize_language(value: str | None) -> str | None:
    """Return ``en`` or ``es`` for a known language name, else None."""
    if not value:
        return None
    candidate = value.strip().lower().replace("-", "_")
    if candidate in _ALIASES:
        return _ALIASES[candidate]
    prefix = candidate.split("_", 1)[0].split(".", 1)[0]
    return _ALIASES.get(prefix)


def windows_language() -> str | None:
    """Return the Windows display language as ``en``/``es``, or None."""
    if sys.platform != "win32":
        return None
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        buffer = ctypes.create_unicode_buffer(85)
        if kernel32.GetUserDefaultLocaleName(buffer, 85) == 0:
            return None
        return normalize_language(buffer.value)
    except (AttributeError, OSError):
        return None


def installer_language() -> str | None:
    """Return the language chosen in the setup wizard, or None."""
    if sys.platform != "win32":
        return None
    try:
        import winreg
    except ImportError:
        return None
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(root, REGISTRY_KEY) as key:
                value, _ = winreg.QueryValueEx(key, REGISTRY_VALUE)
        except OSError:
            continue
        language = normalize_language(str(value))
        if language:
            return language
    return None


def resolve_language(
    explicit: str | None = None,
    installer: str | None = None,
    environment: str | None = None,
    system: str | None = None,
) -> str:
    """Return the language to use, following the documented precedence."""
    for candidate in (
        explicit,
        installer,
        environment,
        system,
    ):
        language = normalize_language(candidate)
        if language in SUPPORTED:
            return language
    return DEFAULT


def detect_language() -> str:
    """Resolve the language from the running system."""
    environment = (
        os.environ.get("MC_LANGUAGE")
        or os.environ.get("LANGUAGE")
        or os.environ.get("LC_ALL")
        or os.environ.get("LC_MESSAGES")
        or os.environ.get("LANG")
    )
    return resolve_language(
        explicit=os.environ.get("MC_LANGUAGE"),
        installer=installer_language(),
        environment=environment,
        system=windows_language(),
    )


def apply_language(language: str) -> None:
    """Export the locale variables gettext and GLib read."""
    tag = "es_ES.UTF-8" if language == "es" else "en_US.UTF-8"
    os.environ["LANG"] = tag
    os.environ["LANGUAGE"] = language
    os.environ["LC_ALL"] = tag
    os.environ["LC_MESSAGES"] = tag
