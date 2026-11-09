# Architecture

Metadata Cleaner for Windows is a thin Windows port around the upstream GTK4
application. The upstream Python source is kept intact where possible; the port
adds relocatable paths, a native launcher, packaging, an updater and tests.

## Runtime layers

```text
MetadataCleaner.exe          native C launcher (installer/launcher)
  └─ runtime/pythonw.exe     bundled Python 3.14 + GTK4/libadwaita
      └─ bin/metadata-cleaner   generated entry point
          └─ metadatacleaner.app.Application
              ├─ ui/          GTK templates and window behavior
              └─ modules/     files, cleaning, language, updater
```

The launcher sets `PATH`, `GSETTINGS_SCHEMA_DIR`, `XDG_DATA_DIRS`,
`GI_TYPELIB_PATH`, `GDK_PIXBUF_MODULE_FILE` and `FONTCONFIG_PATH`, then starts
`runtime\pythonw.exe` with `bin\metadata-cleaner`. It also sets the explicit
AppUserModelID so taskbar pins resolve to the application rather than to
`pythonw.exe`.

## Source map

| Path | Responsibility |
|---|---|
| `src/metadata-cleaner.in` | Meson-generated entry point; relocates data and locale directories, applies the Windows AppUserModelID, initializes gettext. |
| `src/app.py` | `Adw.Application`; actions, windows, update checks and update installation. |
| `src/ui/` | GTK4 templates, main window, settings and file rows. |
| `src/modules/file.py` | A single file: metadata inspection, cleaning and state. |
| `src/modules/filestore.py` | Folder enumeration and batch list model. |
| `src/modules/updater.py` | GitHub Releases selection, SHA-256 verification and installer download. |
| `src/modules/language.py` | Installer/Windows language detection and normalization. |
| `data/` | GSettings schema, icons, UI templates and screenshot. Linux desktop integration (desktop entries, AppStream, D-Bus) is intentionally excluded. |
| `po/` | Spanish catalog (`es.po`), `POTFILES` and `LINGUAS`. English is the source language. |
| `installer/` | Inno Setup script, native launcher and branding. |
| `scripts/` | Payload build and release metadata helpers. |
| `patches/` | Reviewable diffs against the upstream tree and the pinned mat2 version. |
| `tests/` | Static guardrails and runtime tests against a built payload. |

## Cleaning flow

1. The user adds files or folders through the file chooser or drag and drop.
2. `filestore.py` walks directories iteratively with
   `standard::name,standard::type`; this is required for GIO to report a type
   for each child. Unsupported files are ignored.
3. Each file row is added to the model immediately; a shared worker pool asks
   mat2 for metadata and updates the row when the inspection finishes.
4. Cleaning uses mat2's thorough mode by default. The lightweight switch passes
   `lightweight_cleaning=True` to mat2 for the explicit lightweight path.
5. The UI updates each row from the worker result on the GTK main loop.

## Language flow

The installer writes the selected wizard language to
`HKCU\Software\Metadata Cleaner\Language` (`english` or `spanish`). At startup,
`language.py` resolves:

1. `MC_LANGUAGE` override, if set;
2. the installer registry value;
3. the Windows user locale;
4. English.

Only English and Spanish catalogs are shipped. The Ubuntu-style
`share/locale` directory is populated with `es` only; upgrades delete stale
locale directories before installing the new payload.

## Update flow

1. At startup (at most once per day) or from the menu, the app fetches the
   GitHub Releases API.
2. `pick_update` accepts three- or four-component tags and selects the newest
   release with a matching x64 installer and a SHA-256 digest or sidecar.
3. A dialog offers **Update now** or **Later**. Accepting downloads the
   installer to the user's temporary directory, verifies its SHA-256, starts
   the installer and quits the app.
4. The installer keeps the same `AppId`, reuses the previous directory and
   preserves settings, so no uninstall is required.

## Distribution

The Inno Setup payload contains the application prefix, a pruned UCRT64 runtime,
exiftool and ffmpeg. `scripts/build-windows.sh` writes all build output outside
the repository. The GitHub Actions release workflow builds and tests the payload
on `windows-latest`, compiles the installer, writes checksums and publishes the
release. See [`build.md`](build.md) and
[`versioning.md`](versioning.md#releasing-a-port-revision).

## Design boundaries

- Keep Windows-specific behavior in the smallest possible patch; prefer a
  guarded branch in `metadata-cleaner.in`, `file.py` or `filestore.py` over a
  fork of the UI.
- The updater must remain importable without GTK so its selection and checksum
  logic can be tested headlessly.
- Never write build output, installers, caches or downloaded updates into the
  repository.
- `Metadata Cleaner` is a proper noun and is never translated; English and
  Spanish UI strings keep it verbatim.
- File and directory names are English, lowercase except for conventional
  uppercase documents (`README.md`, `LICENSE`, `AGENTS.md`).
- The Windows payload must not include Linux desktop integration, Flatpak,
  Flathub, AppStream or D-Bus files.
