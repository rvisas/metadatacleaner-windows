# Windows installer

The Windows deliverable is an Inno Setup installer. It bundles the application,
the GTK/Python runtime and the external tools, and creates Start Menu/Desktop
shortcuts plus an uninstaller.

## Payload layout

`scripts/build-windows.sh` writes the payload to a temporary directory outside
the repository by default. Its layout is:

```
payload\
  MetadataCleaner.exe      native launcher
  runtime\                 Python, GTK/Poppler DLLs, typelibs, schemas
  share\                   application data, icons, locales
  tools\exiftool\          exiftool.exe and its files
  tools\ffmpeg\            ffmpeg.exe (runtime DLLs come from runtime\bin)
```

The build is reproducible from source but it is deliberately not stored in the
workspace: the installer is produced by the GitHub release workflow, and the
local build directory is disposable.

## Launcher

`launcher\MetadataCleaner.c` is a small native Win32 launcher with no .NET
dependency. It sets `PATH`, `GSETTINGS_SCHEMA_DIR`, `XDG_DATA_DIRS`
(`share;runtime\share`), `GI_TYPELIB_PATH` and `GDK_PIXBUF_MODULE_FILE`, then
starts `runtime\bin\pythonw.exe` with `bin\metadata-cleaner` and forwards any
command-line arguments. Its working directory is `runtime\`, which is where the
gdk-pixbuf loader cache paths are rooted.

Build it with MSYS2 UCRT64:

```bash
cd installer\launcher
windres MetadataCleaner.rc -O coff -o launcher.o
gcc -municode -mwindows -static -O2 -s -o "<build>\payload\MetadataCleaner.exe" MetadataCleaner.c launcher.o
```

`windres` embeds `branding\metadatacleaner-windows.ico` into the launcher.

The `[Icons]` entries set `AppUserModelID` to
`io.gitlab.metadatacleaner.metadatacleaner` and use the launcher as their icon.
The application sets the same ID on its own process before creating the window,
so a taskbar pin resolves to `MetadataCleaner.exe` instead of the underlying
`pythonw.exe`.

## Build the installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php) 6.3 or newer.
2. Build the payload with `scripts/build-windows.sh`; its default output is
   outside the repository (use `BUILD_ROOT` to choose the directory).
3. Compile with both directories explicit:

   ```bat
   iscc /DAppVersion=4.0.1.3 /DPayloadDir=<build>\payload /DOutputDir=<build>\installer installer\metadatacleaner.iss
   ```

   The installer is written to `<build>\installer`, never to the repository.
   In GitHub Actions the same steps run automatically and publish the asset.

The script installs per-user by default (`PrivilegesRequired=lowest`); the user
can choose an all-users install from the privileges dialog. It targets Windows 10
2004+ and Windows 11, x64.

The installer uses one stable `AppId`, so running a newer installer updates the
existing installation in place: no uninstall step is needed and settings are
kept. The welcome page reports the installed and new versions when it detects a
previous installation. The setup wizard is localized in English and Spanish
only.

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

Signing is handled through a code-signing provider for this open-source
project; SignPath Foundation is the first option. See
[`../docs/code-signing.md`](../docs/code-signing.md) for the alternatives and
current status. Once a provider is approved, uncomment `SignTool` and
`SignedUninstaller` in the `.iss` and sign both the installer and the
uninstaller. Do not commit certificates or private keys.
