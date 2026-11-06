/* SPDX-FileCopyrightText: 2026 Ronny Visa */
/* SPDX-License-Identifier: GPL-3.0-or-later */

#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>

#define BUFFER_SIZE 32768

static void parent_directory(wchar_t *path)
{
    wchar_t *separator = wcsrchr(path, L'\\');
    if (separator != NULL)
    {
        *separator = L'\0';
    }
}

static void join_path(wchar_t *output, size_t size, const wchar_t *base, const wchar_t *child)
{
    swprintf(output, size, L"%ls\\%ls", base, child);
}

static void set_environment(const wchar_t *name, const wchar_t *value)
{
    SetEnvironmentVariableW(name, value);
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR command_line, int show_command)
{
    wchar_t root[MAX_PATH];
    if (GetModuleFileNameW(NULL, root, MAX_PATH) == 0)
    {
        return 1;
    }
    parent_directory(root);

    wchar_t runtime[MAX_PATH];
    wchar_t runtime_bin[MAX_PATH];
    wchar_t runtime_share[MAX_PATH];
    wchar_t share[MAX_PATH];
    wchar_t tools[MAX_PATH];
    wchar_t python[MAX_PATH];
    wchar_t script[MAX_PATH];
    wchar_t schemas[MAX_PATH];
    wchar_t typelibs[MAX_PATH];
    wchar_t pixbuf_cache[MAX_PATH];
    wchar_t fonts[MAX_PATH];
    wchar_t data_dirs[BUFFER_SIZE];
    wchar_t old_path[BUFFER_SIZE];
    wchar_t new_path[BUFFER_SIZE];
    wchar_t arguments[BUFFER_SIZE];

    join_path(runtime, MAX_PATH, root, L"runtime");
    join_path(runtime_bin, MAX_PATH, runtime, L"bin");
    join_path(runtime_share, MAX_PATH, runtime, L"share");
    join_path(share, MAX_PATH, root, L"share");
    join_path(tools, MAX_PATH, root, L"tools");
    join_path(python, MAX_PATH, runtime_bin, L"pythonw.exe");
    join_path(script, MAX_PATH, root, L"bin\\metadata-cleaner");
    join_path(schemas, MAX_PATH, share, L"glib-2.0\\schemas");
    join_path(typelibs, MAX_PATH, runtime, L"lib\\girepository-1.0");
    join_path(pixbuf_cache, MAX_PATH, runtime, L"lib\\gdk-pixbuf-2.0\\2.10.0\\loaders.cache");
    join_path(fonts, MAX_PATH, runtime, L"etc\\fonts");

    swprintf(data_dirs, BUFFER_SIZE, L"%ls;%ls", share, runtime_share);

    DWORD path_length = GetEnvironmentVariableW(L"PATH", old_path, BUFFER_SIZE);
    if (path_length == 0 || path_length >= BUFFER_SIZE)
    {
        old_path[0] = L'\0';
    }

    swprintf(
        new_path,
        BUFFER_SIZE,
        L"%ls;%ls\\exiftool;%ls\\ffmpeg;%ls",
        runtime_bin,
        tools,
        tools,
        old_path
    );

    set_environment(L"PATH", new_path);
    set_environment(L"GSETTINGS_SCHEMA_DIR", schemas);
    set_environment(L"XDG_DATA_DIRS", data_dirs);
    set_environment(L"GI_TYPELIB_PATH", typelibs);
    set_environment(L"GDK_PIXBUF_MODULE_FILE", pixbuf_cache);
    set_environment(L"FONTCONFIG_PATH", fonts);
    set_environment(L"PYTHONUTF8", L"1");

    if (command_line != NULL && command_line[0] != L'\0')
    {
        swprintf(arguments, BUFFER_SIZE, L"\"%ls\" \"%ls\" %ls", python, script, command_line);
    }
    else
    {
        swprintf(arguments, BUFFER_SIZE, L"\"%ls\" \"%ls\"", python, script);
    }

    STARTUPINFOW startup;
    PROCESS_INFORMATION process;
    ZeroMemory(&startup, sizeof(startup));
    startup.cb = sizeof(startup);
    ZeroMemory(&process, sizeof(process));

    if (!CreateProcessW(python, arguments, NULL, NULL, FALSE, 0, NULL, runtime, &startup, &process))
    {
        wchar_t message[1024];
        swprintf(
            message,
            1024,
            L"No se pudo iniciar Metadata Cleaner.\n\n%ls\n\nError %lu.",
            python,
            GetLastError()
        );
        MessageBoxW(NULL, message, L"Metadata Cleaner", MB_ICONERROR | MB_OK);
        return 1;
    }

    CloseHandle(process.hThread);
    CloseHandle(process.hProcess);
    return 0;
}
