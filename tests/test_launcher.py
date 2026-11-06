# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Integration test for the native launcher.

Compiles a fake pythonw.exe that records the command line, working directory
and environment, then runs the real launcher against a temporary payload.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "installer" / "launcher" / "MetadataCleaner.c"

FAKE_PYTHON = r"""
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <stdio.h>
#include <wchar.h>

static void write_env(FILE *file, const wchar_t *name)
{
    wchar_t value[32768];
    DWORD length = GetEnvironmentVariableW(name, value, 32768);
    fwprintf(file, L"%ls=%ls\n", name, length ? value : L"");
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR command_line, int show_command)
{
    wchar_t executable[MAX_PATH];
    if (GetModuleFileNameW(NULL, executable, MAX_PATH) == 0)
    {
        return 2;
    }
    wchar_t *separator = wcsrchr(executable, L'\\');
    if (separator != NULL)
    {
        *separator = L'\0';
    }

    wchar_t result_path[MAX_PATH];
    swprintf(result_path, MAX_PATH, L"%ls\\result.txt", executable);
    FILE *file = _wfopen(result_path, L"w");
    if (file == NULL)
    {
        return 3;
    }

    wchar_t directory[32768];
    GetCurrentDirectoryW(32768, directory);

    fwprintf(file, L"CMDLINE=%ls\n", GetCommandLineW());
    fwprintf(file, L"CWD=%ls\n", directory);
    write_env(file, L"PATH");
    write_env(file, L"GSETTINGS_SCHEMA_DIR");
    write_env(file, L"XDG_DATA_DIRS");
    write_env(file, L"GI_TYPELIB_PATH");
    write_env(file, L"GDK_PIXBUF_MODULE_FILE");
    write_env(file, L"FONTCONFIG_PATH");
    fclose(file);
    return 0;
}
"""


def normalize(value: str) -> str:
    """Compare Windows paths regardless of slash direction or case."""
    return os.path.normcase(os.path.normpath(value))


@unittest.skipUnless(os.name == "nt", "Windows-only launcher test")
class LauncherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gcc = shutil.which("gcc")
        if not self.gcc:
            self.skipTest("gcc not found; run this test inside MSYS2 UCRT64")

    def test_launcher_sets_environment_and_forwards_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runtime = root / "runtime"
            runtime_bin = runtime / "bin"
            runtime_bin.mkdir(parents=True)
            (root / "bin").mkdir()
            (root / "tools" / "exiftool").mkdir(parents=True)
            (root / "tools" / "ffmpeg").mkdir(parents=True)
            (root / "share" / "glib-2.0" / "schemas").mkdir(parents=True)

            script = root / "bin" / "metadata-cleaner"
            script.write_text("# fake entry point\n", encoding="utf-8")

            fake_source = root / "fake_python.c"
            fake_source.write_text(FAKE_PYTHON, encoding="utf-8")
            subprocess.run(
                [
                    self.gcc,
                    "-municode",
                    "-mwindows",
                    "-static",
                    "-O2",
                    "-s",
                    "-o",
                    str(runtime_bin / "pythonw.exe"),
                    str(fake_source),
                ],
                check=True,
                timeout=120,
            )

            launcher_source = root / "launcher.c"
            shutil.copyfile(LAUNCHER, launcher_source)
            launcher = root / "MetadataCleaner.exe"
            subprocess.run(
                [
                    self.gcc,
                    "-municode",
                    "-mwindows",
                    "-static",
                    "-O2",
                    "-s",
                    "-o",
                    str(launcher),
                    str(launcher_source),
                ],
                check=True,
                timeout=120,
            )

            subprocess.run(
                [str(launcher), "--flag", "value with spaces"],
                check=True,
                timeout=20,
            )

            result_file = runtime_bin / "result.txt"
            deadline = time.time() + 10
            while not result_file.exists() and time.time() < deadline:
                time.sleep(0.1)

            self.assertTrue(result_file.exists(), "fake pythonw.exe did not run")
            result = result_file.read_text(encoding="utf-8", errors="replace")
            values = dict(
                line.split("=", 1)
                for line in result.splitlines()
                if "=" in line
            )

            self.assertIn(str(script).replace("/", "\\"), values["CMDLINE"])
            self.assertIn("--flag", values["CMDLINE"])
            self.assertIn("value with spaces", values["CMDLINE"])
            self.assertEqual(
                normalize(values["CWD"]),
                normalize(str(runtime)),
            )
            self.assertEqual(
                normalize(values["PATH"].split(";")[0]),
                normalize(str(runtime_bin)),
            )
            self.assertIn(
                normalize(str(root / "tools" / "exiftool")),
                [normalize(part) for part in values["PATH"].split(";")],
            )
            self.assertIn(
                normalize(str(root / "tools" / "ffmpeg")),
                [normalize(part) for part in values["PATH"].split(";")],
            )
            self.assertEqual(
                normalize(values["GSETTINGS_SCHEMA_DIR"]),
                normalize(str(root / "share" / "glib-2.0" / "schemas")),
            )
            data_dirs = [
                normalize(part)
                for part in values["XDG_DATA_DIRS"].split(";")
            ]
            self.assertIn(normalize(str(root / "share")), data_dirs)
            self.assertIn(normalize(str(runtime / "share")), data_dirs)
            self.assertEqual(
                normalize(values["GI_TYPELIB_PATH"]),
                normalize(str(runtime / "lib" / "girepository-1.0")),
            )
            self.assertEqual(
                normalize(values["GDK_PIXBUF_MODULE_FILE"]),
                normalize(
                    str(
                        runtime
                        / "lib"
                        / "gdk-pixbuf-2.0"
                        / "2.10.0"
                        / "loaders.cache"
                    )
                ),
            )
            self.assertEqual(
                normalize(values["FONTCONFIG_PATH"]),
                normalize(str(runtime / "etc" / "fonts")),
            )


if __name__ == "__main__":
    unittest.main()
