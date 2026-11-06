# metadatacleaner-windows

Unofficial Windows 10/11 port of [Metadata Cleaner](https://gitlab.com/metadatacleaner/metadatacleaner), the GTK4 application for viewing and removing metadata from files.

> **Status:** early port for Windows 10/11 x64. The app builds and runs on Windows 11; metadata cleaning has been verified on JPEG, PDF, DOCX and MP4. The Inno Setup installer is in progress.

## Why this exists

I care about metadata privacy. For years, Metadata Cleaner was one of the first tools I installed on every Linux machine I used: a small, focused app that showed me what a file was carrying and let me remove it before sharing it.

When my work brought me back to Windows 11, I looked for the same experience and couldn't find it. There were other tools, but none felt like the app I had used for years. So I built the version I was missing: the same GTK workflow, running natively on Windows.

This repository is that port. It is intentionally kept close to the maintained upstream so it can follow its releases instead of drifting into a separate product.

## What it does

- View metadata before cleaning.
- Remove metadata from images, documents, audio and video through [mat2](https://github.com/jvoisin/mat2).
- Add individual files or whole folders; drag and drop is supported.
- Works offline: no telemetry, no uploads.
- Thorough cleaning by default, which is the mode that removes the most metadata.

As in upstream, cleaning rewrites the selected file: the app works on a temporary copy and replaces the original when the process finishes. Keep backups of anything irreplaceable.

## Windows-specific changes

This port carries a small set of patches over upstream. They live in `patches/` and are described in [`UPSTREAM.md`](UPSTREAM.md):

1. Relocatable install paths: the app locates its data relative to the executable instead of a POSIX prefix.
2. Windows home paths: `C:\Users\...` is not a valid regular expression, so the home check uses `str.startswith`.
3. The Flatpak document-portal xattr query is skipped on Windows, where it does not exist.
4. PDF URIs are built with `Path.as_uri()` (`file:///C:/...`), which fixes drive letters and names containing `#`, spaces or accents.
5. The temporary file descriptor used by the PDF writer is closed; Windows cannot delete an open file.
6. Archive-based formats (DOCX, ODT, EPUB) use `os.replace` and writable permissions, so existing members are replaced and temporary folders can be removed.

## Supported files

Through mat2: JPEG, PNG, TIFF, WebP, AVIF, HEIC/HEIF, GIF and BMP; PDF; DOCX/XLSX/PPTX, ODT/ODS/ODP and EPUB; MP3, FLAC, OGG, WAV and M4A; MP4, MKV, MOV, AVI and WebM. Video also needs ffmpeg; some image formats need exiftool.

## Build and run

The app is GTK4 / libadwaita / PyGObject and builds on Windows with MSYS2 UCRT64. The tested steps, package list and runtime environment are in [`docs/BUILD.md`](docs/BUILD.md).

Short version: install the UCRT64 GTK/Python stack, `pip install mat2==0.15.0 --no-deps`, configure with meson, install, then run `python.exe bin/metadata-cleaner` with `GSETTINGS_SCHEMA_DIR` pointing at the installed schemas.

## Upstream tracking

- Upstream: https://gitlab.com/metadatacleaner/metadatacleaner
- This repository is maintained as a **patch set** over a pinned upstream release, not as a permanent fork with shared Git history.
- `patches/` contains the Windows delta; the port source lives on `main`.
- When upstream publishes a release, the patches are re-applied to the new tree, the app is rebuilt, and the format tests are re-run. The procedure is in [`UPSTREAM.md`](UPSTREAM.md).

The goal is to keep the Windows delta small and reviewable so it can follow upstream releases without becoming a separate product.

## Packaging

The Windows deliverable is an Inno Setup installer (`MetadataCleaner-Setup-x.y.z.exe`). It bundles the application, the GTK/Python runtime and the external tools, and creates Start Menu/Desktop shortcuts plus an uninstaller. A separate portable ZIP is not part of the current scope.

## License

GPL-3.0-or-later, the same license as upstream. See [`LICENSE`](LICENSE) and [`LICENSES/`](LICENSES). mat2 is LGPL-3.0; exiftool, poppler and ffmpeg keep their own licenses.

This is an unofficial port, not affiliated with or endorsed by the upstream maintainers. Metadata removal is best-effort: no tool can guarantee that every identifying byte, watermark or derived signal has been removed. Inspect important files before publishing them.
