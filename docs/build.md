# Building on Windows

These are the steps that were actually used to build and run the app on Windows
11 with MSYS2 UCRT64. They are intentionally explicit: PyGObject is not a
`pip install` away on Windows, and the GTK stack comes from the MSYS2
repository.

## 1. Toolchain

Install MSYS2 and open a **UCRT64** shell. Install the build tools and the
runtime:

```bash
pacman -S --needed meson ninja gettext pkgconf glib2 glib2-devel libxml2 \
  mingw-w64-ucrt-x86_64-gtk4 \
  mingw-w64-ucrt-x86_64-libadwaita \
  mingw-w64-ucrt-x86_64-python \
  mingw-w64-ucrt-x86_64-python-pip \
  mingw-w64-ucrt-x86_64-python-gobject \
  mingw-w64-ucrt-x86_64-python-cairo \
  mingw-w64-ucrt-x86_64-python-mutagen \
  mingw-w64-ucrt-x86_64-poppler \
  mingw-w64-ucrt-x86_64-librsvg \
  mingw-w64-ucrt-x86_64-gdk-pixbuf2 \
  mingw-w64-ucrt-x86_64-ffmpeg \
  mingw-w64-ucrt-x86_64-adwaita-icon-theme \
  mingw-w64-ucrt-x86_64-hicolor-icon-theme \
  mingw-w64-ucrt-x86_64-shared-mime-info \
  mingw-w64-ucrt-x86_64-gcc \
  mingw-w64-ucrt-x86_64-meson \
  mingw-w64-ucrt-x86_64-ninja
```

The Windows port does not install Linux `.desktop`, AppStream or D-Bus files,
so it does not need `appstream`, `desktop-file-utils` or their validation
tools.

## 2. mat2 and exiftool

```bash
export PATH=/ucrt64/bin:$PATH
python -m pip install --no-deps --break-system-packages mat2==0.15.0
```

Download the official Windows exiftool zip from <https://exiftool.org/> and
rename `exiftool(-k).exe` to `exiftool.exe`. mat2 finds it through `PATH`.

ffmpeg and poppler come from the UCRT64 packages installed above.

## 3. Build

meson on MSYS rejects `C:/...` as an absolute prefix, so configure with a POSIX
path and let the app relocate itself at runtime:

```bash
export PATH=/usr/local/bin:$PATH:/ucrt64/bin
export GETTEXTDATADIR=/usr/share/gettext

meson setup /c/mc-build/build --prefix=/c/mc-port/app -Ddevel=false
meson compile -C /c/mc-build/build
meson install -C /c/mc-build/build
```

The install step runs `glib-compile-schemas` and `gtk4-update-icon-cache`.
There is no `update-desktop-database` step because the Windows payload contains
no Linux desktop entry.

## 4. Run

```bash
export PATH=/ucrt64/bin:/path/to/exiftool:$PATH
export GSETTINGS_SCHEMA_DIR='C:/mc-port/app/share/glib-2.0/schemas'
export XDG_DATA_DIRS='C:/mc-port/app/share;C:/msys64/ucrt64/share'
cd /c/mc-port/app
python.exe bin/metadata-cleaner
```

`Gio.Settings` needs the compiled schema directory. `XDG_DATA_DIRS` lets GTK find
the icon themes from the UCRT64 prefix.

## 5. Smoke test without the GUI

The app's own `File` class can be exercised headlessly:

```python
import sys, os
sys.path.insert(0, r"C:\mc-port\app\share\metadata-cleaner")
from gi.repository import Gio
from metadatacleaner.modules.file import File, FileState

path = r"C:\path\to\sample.jpg"
f = File(Gio.File.new_for_path(path))
f.check_metadata()
print(f.state, f.error)
f.clean()
print(f.state, f.error)
```

`HAS_METADATA` is `8` and `CLEANED` is `11`. `total_metadata` is updated through
`GLib.idle_add`, so it stays `0` until the main loop runs; use `f.metadata` to
inspect the entries in a headless test.

## 6. Payload

The installer payload bundles the app prefix and a pruned copy of the UCRT64
prefix. Start from a working build, then assemble it outside the repository:

```bash
cp -a /c/mc-ephemeral/app/. /c/mc-ephemeral/payload/
cp -a /c/mc-ephemeral/msys64/ucrt64 /c/mc-ephemeral/payload/runtime
cp -a /c/mc-ephemeral/tools/exiftool /c/mc-ephemeral/payload/tools/exiftool
mkdir -p /c/mc-ephemeral/payload/tools/ffmpeg
cp /c/mc-ephemeral/payload/runtime/bin/ffmpeg.exe /c/mc-ephemeral/payload/tools/ffmpeg/
```

Prune development material from `runtime`: `include/`, `lib/*.a`,
`lib/*.dll.a`, `share/doc`, `share/man`, `share/gtk-doc`, `share/info`,
`share/locale`, `share/gir-1.0`, the Python `test`/`tkinter`/`idlelib` trees,
and every `bin/*.exe` except `python.exe`, `pythonw.exe`,
`gspawn-win64-helper*.exe`, `gdbus.exe` and `gdk-pixbuf-query-loaders.exe`.
Keep the DLLs, typelibs, schemas, icon themes and gdk-pixbuf loaders.

Merge the application schema into the runtime schema directory, then compile it
once:

```bash
cp -f /c/mc-ephemeral/payload/runtime/share/glib-2.0/schemas/*.xml \
      /c/mc-ephemeral/payload/share/glib-2.0/schemas/
glib-compile-schemas /c/mc-ephemeral/payload/share/glib-2.0/schemas
```

The payload layout is:

```text
payload\
  MetadataCleaner.exe      native launcher
  runtime\                 Python, GTK/Poppler DLLs, typelibs, schemas
  share\                   application data, icons, locales
  tools\exiftool\          exiftool.exe and its files
  tools\ffmpeg\            ffmpeg.exe (runtime DLLs come from runtime\bin)
```

### Launcher

`installer\launcher\MetadataCleaner.c` is a small native Win32 launcher with no
.NET dependency. It sets `PATH`, `GSETTINGS_SCHEMA_DIR`, `XDG_DATA_DIRS`
(`share;runtime\share`), `GI_TYPELIB_PATH` and `GDK_PIXBUF_MODULE_FILE`, then
starts `runtime\bin\pythonw.exe` with `bin\metadata-cleaner` and forwards any
command-line arguments. Its working directory is `runtime\`, which is where the
gdk-pixbuf loader cache paths are rooted.

Build it with MSYS2 UCRT64:

```bash
cd installer/launcher
windres MetadataCleaner.rc -O coff -o launcher.o
gcc -municode -mwindows -static -O2 -s \
  -o "<build>/payload/MetadataCleaner.exe" MetadataCleaner.c launcher.o
```

`windres` embeds `branding/metadatacleaner-windows.ico` into the launcher.
`MetadataCleaner.rc` also carries a `VERSIONINFO` block with the product name,
file version and product version. Keep its `MC_VERSION` and
`MC_VERSION_STRING` values in sync with the release;
`python scripts/versioning.py check` rejects drift.

The `[Icons]` entries in the installer set `AppUserModelID` to
`io.gitlab.metadatacleaner.metadatacleaner` and use the launcher as their icon.
The application sets the same ID on its own process before creating the window,
so a taskbar pin resolves to `MetadataCleaner.exe` instead of the underlying
`pythonw.exe`.

### Icon

`installer/branding/metadatacleaner-windows.ico` is the Windows icon used by
the installer and the app. It is generated from the unmodified upstream icon
(`data/icons/io.gitlab.metadatacleaner.metadatacleaner.svg`) and contains 16,
24, 32, 48, 64, 128 and 256 px images. The artwork is CC-BY-SA-4.0; see the
`.license` file next to the ICO.

To regenerate it:

```bash
resvg --width 256 data/icons/io.gitlab.metadatacleaner.metadatacleaner.svg icon-256.png
python -c "from PIL import Image; Image.open('icon-256.png').convert('RGBA').save('metadatacleaner-windows.ico', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
```

### Installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php) 6.3 or newer.
2. Build the payload with `scripts/build-windows.sh`; its default output is
   outside the repository (use `BUILD_ROOT` to choose the directory).
3. Compile with both directories explicit:

   ```bat
   iscc /DAppVersion=4.0.1.7 /DPayloadDir=<build>\payload /DOutputDir=<build>\installer installer\metadatacleaner.iss
   ```

   The installer is written to `<build>\installer`, never to the repository.
   In GitHub Actions the same steps run automatically and publish the asset.

The script installs per-user by default (`PrivilegesRequired=lowest`); the user
can choose an all-users install from the privileges dialog. It targets Windows
10 2004+ and Windows 11, x64.

The installer uses one stable `AppId`, so running a newer installer updates the
existing installation in place: no uninstall step is needed and settings are
kept. The welcome page reports the installed and new versions when it detects a
previous installation. The setup wizard is localized in English and Spanish
only.

Signing is handled through SignPath Foundation once the project is approved.
See [`code-signing.md`](code-signing.md) for the policy and current status.

## 7. Known build notes

- Use one MSYS2 environment consistently: UCRT64. Mixing MINGW64 and UCRT64
  packages produces DLL/typelib mismatches.
- `pip install pygobject` is not the Windows path; use the MSYS2 package.
- A DLL without its `.typelib` fails at import. `Poppler-0.18.typelib` is the one
  mat2 needs for PDF support.
- The build currently lives outside the repository (for example `C:\mc-build`);
  the repository only contains source, patches and documentation.
