# Windows installer

The Windows deliverable is an Inno Setup installer. It bundles the application,
the GTK/Python runtime and the external tools, and creates Start Menu/Desktop
shortcuts plus an uninstaller.

## Payload layout

The script expects the payload under `dist\payload`:

```
dist\payload\
  MetadataCleaner.exe      native launcher
  runtime\                 Python, GTK/Poppler DLLs, typelibs, schemas
  share\                   application data, icons, locales
  tools\exiftool\          exiftool.exe and its files
  tools\ffmpeg\            ffmpeg.exe and its DLLs
```

`MetadataCleaner.exe` is the entry point referenced by the shortcuts and the
uninstaller. The payload is produced by the build/packaging step; see
[`../docs/BUILD.md`](../docs/BUILD.md).

## Build the installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php) 6.3 or newer.
2. Build `dist\payload`.
3. Compile:

   ```bat
   iscc installer\metadatacleaner.iss
   ```

   The result is `dist\installer\MetadataCleaner-Setup-4.0.1.exe`.

The script installs per-user by default (`PrivilegesRequired=lowest`); the user
can choose an all-users install from the privileges dialog. It targets Windows 10
2004+ and Windows 11, x64.

## Icon

`branding\metadatacleaner-windows.ico` is the Windows icon used by the installer
and the app. It is generated from the unmodified upstream icon
(`data/icons/io.gitlab.metadatacleaner.metadatacleaner.svg`) and contains 16, 24,
32, 48, 64, 128 and 256 px images.

The icon is intentionally unchanged: the Windows identity comes from the
application name, the installer and the About dialog. The artwork is
CC-BY-SA-4.0; see the `.license` file next to the ICO.

To regenerate it, render the upstream SVG at 256 px and pack the sizes with
Pillow:

```bash
resvg --width 256 ../data/icons/io.gitlab.metadatacleaner.metadatacleaner.svg icon-256.png
python -c "from PIL import Image; Image.open('icon-256.png').convert('RGBA').save('metadatacleaner-windows.ico', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```

## Code signing

Signing is handled through SignPath Foundation for this open-source project. See
[`../docs/SIGNPATH.md`](../docs/SIGNPATH.md). Once the project is approved,
uncomment `SignTool` and `SignedUninstaller` in the `.iss` and sign both the
installer and the uninstaller. Do not commit certificates or private keys.
