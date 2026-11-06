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
  mingw-w64-ucrt-x86_64-appstream \
  mingw-w64-ucrt-x86_64-adwaita-icon-theme \
  mingw-w64-ucrt-x86_64-hicolor-icon-theme \
  mingw-w64-ucrt-x86_64-shared-mime-info \
  mingw-w64-ucrt-x86_64-desktop-file-utils
```

`appstream` is needed at build time because `msgfmt` uses its `metainfo.its`
rules. Copy them where the MSYS `msgfmt` can find them:

```bash
cp -f /ucrt64/share/gettext/its/* /usr/share/gettext/its/
```

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

The install step runs `glib-compile-schemas`, `gtk4-update-icon-cache` and
`update-desktop-database`. If the last one is missing, either install the UCRT64
package (`mingw-w64-ucrt-x86_64-desktop-file-utils`) or provide a no-op
executable; it only updates a Linux desktop database.

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

## 6. Known build notes

- Use one MSYS2 environment consistently: UCRT64. Mixing MINGW64 and UCRT64
  packages produces DLL/typelib mismatches.
- `pip install pygobject` is not the Windows path; use the MSYS2 package.
- A DLL without its `.typelib` fails at import. `Poppler-0.18.typelib` is the one
  mat2 needs for PDF support.
- The build currently lives outside the repository (for example `C:\mc-build`);
  the repository only contains source, patches and documentation.
