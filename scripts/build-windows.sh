#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the Windows payload from an MSYS2 UCRT64 shell. The workflow installs
# the toolchain; this script only assumes the UCRT64 packages are present.
#
# Usage: VERSION=4.0.1 ./scripts/build-windows.sh

set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VERSION="${VERSION:-4.0.1}"
MINGW_PREFIX="${MINGW_PREFIX:-/ucrt64}"
PYTHON="$MINGW_PREFIX/bin/python.exe"
BUILD_DIR="${BUILD_DIR:-$ROOT/dist/build}"
PAYLOAD_DIR="${PAYLOAD_DIR:-$ROOT/dist/payload}"
TOOLS_DIR="$ROOT/dist/tools"
EXIFTOOL_VERSION="${EXIFTOOL_VERSION:-13.60}"

if [[ ! -x "$PYTHON" ]]; then
    echo "error: $PYTHON not found; run this from MSYS2 UCRT64" >&2
    exit 1
fi

echo "==> Preparing ${PAYLOAD_DIR}"
rm -rf "$BUILD_DIR" "$PAYLOAD_DIR"
mkdir -p "$BUILD_DIR" "$PAYLOAD_DIR" "$TOOLS_DIR"

# msgfmt needs the AppStream ITS rules from the UCRT64 prefix.
cp -f "$MINGW_PREFIX/share/gettext/its/"* /usr/share/gettext/its/ 2>/dev/null || true

echo "==> Installing mat2"
"$PYTHON" -m pip install --no-deps --break-system-packages "mat2==0.15.0"
PY_VERSION=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
SITE_PACKAGES="$MINGW_PREFIX/lib/python$PY_VERSION/site-packages"
(
    cd "$SITE_PACKAGES"
    patch -p1 < "$ROOT/patches/0002-mat2-windows.patch"
)

echo "==> Building the application"
export PATH="$MINGW_PREFIX/bin:/usr/local/bin:$PATH"
export GETTEXTDATADIR=/usr/share/gettext
meson setup "$BUILD_DIR" --prefix="$PAYLOAD_DIR" -Ddevel=false
meson compile -C "$BUILD_DIR"
meson install -C "$BUILD_DIR"

echo "==> Copying and pruning the runtime"
cp -a "$MINGW_PREFIX" "$PAYLOAD_DIR/runtime"
rm -rf \
    "$PAYLOAD_DIR/runtime/include" \
    "$PAYLOAD_DIR/runtime/lib/gcc" \
    "$PAYLOAD_DIR/runtime/libexec/gcc"
find "$PAYLOAD_DIR/runtime/lib" -maxdepth 1 -type f \
    \( -name '*.a' -o -name '*.dll.a' \) -delete
rm -rf \
    "$PAYLOAD_DIR/runtime/lib/terminfo" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/test" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/tests" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/idlelib" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/tkinter" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/ensurepip" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/lib2to3" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/pydoc_data" \
    "$PAYLOAD_DIR/runtime/lib/python$PY_VERSION/turtledemo" \
    "$PAYLOAD_DIR/runtime/share/doc" \
    "$PAYLOAD_DIR/runtime/share/man" \
    "$PAYLOAD_DIR/runtime/share/gtk-doc" \
    "$PAYLOAD_DIR/runtime/share/info" \
    "$PAYLOAD_DIR/runtime/share/terminfo" \
    "$PAYLOAD_DIR/runtime/share/zoneinfo" \
    "$PAYLOAD_DIR/runtime/share/locale" \
    "$PAYLOAD_DIR/runtime/share/gir-1.0"
find "$PAYLOAD_DIR/runtime/bin" -maxdepth 1 -type f -name '*.exe' \
    ! -name 'python.exe' \
    ! -name 'pythonw.exe' \
    ! -name 'gspawn-win64-helper.exe' \
    ! -name 'gspawn-win64-helper-console.exe' \
    ! -name 'gdbus.exe' \
    ! -name 'gdk-pixbuf-query-loaders.exe' \
    -delete
find "$PAYLOAD_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +

echo "==> Adding external tools"
mkdir -p "$PAYLOAD_DIR/tools/ffmpeg"
cp -f "$MINGW_PREFIX/bin/ffmpeg.exe" "$PAYLOAD_DIR/tools/ffmpeg/"

if [[ ! -x "$TOOLS_DIR/exiftool/exiftool.exe" ]]; then
    echo "==> Downloading exiftool $EXIFTOOL_VERSION"
    curl -fL --retry 3 --max-time 300 \
        -o "$TOOLS_DIR/exiftool.zip" \
        "https://sourceforge.net/projects/exiftool/files/exiftool-${EXIFTOOL_VERSION}_64.zip/download"
    "$PYTHON" -m zipfile -e "$TOOLS_DIR/exiftool.zip" "$TOOLS_DIR"
    mv "$TOOLS_DIR/exiftool-${EXIFTOOL_VERSION}_64" "$TOOLS_DIR/exiftool"
    cp "$TOOLS_DIR/exiftool/exiftool(-k).exe" "$TOOLS_DIR/exiftool/exiftool.exe"
    rm -f "$TOOLS_DIR/exiftool.zip"
fi
cp -a "$TOOLS_DIR/exiftool" "$PAYLOAD_DIR/tools/exiftool"

echo "==> Merging GSettings schemas"
cp -f "$PAYLOAD_DIR/runtime/share/glib-2.0/schemas/"*.xml \
    "$PAYLOAD_DIR/share/glib-2.0/schemas/"
glib-compile-schemas "$PAYLOAD_DIR/share/glib-2.0/schemas"

echo "==> Building the launcher"
(
    cd "$ROOT/installer/launcher"
    windres MetadataCleaner.rc -O coff -o "$BUILD_DIR/launcher.o"
    gcc -municode -mwindows -static -O2 -s \
        -o "$PAYLOAD_DIR/MetadataCleaner.exe" \
        MetadataCleaner.c "$BUILD_DIR/launcher.o"
)

echo "==> Payload ready: $PAYLOAD_DIR ($(du -sh "$PAYLOAD_DIR" | cut -f1))"
