# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Naming and checksum helpers shared by the release workflow and tests."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

APP_NAME = "MetadataCleaner"
_VERSION = re.compile(r"^\d+\.\d+\.\d+(?:\.\d+)?$")


def _validate_version(version: str) -> str:
    """Reject versions that cannot be used in a tag or file name."""
    if _VERSION.fullmatch(version) is None:
        raise ValueError(f"invalid port version: {version!r}")
    return version


def installer_filename(version: str) -> str:
    """Return the release asset name for a Windows installer."""
    return f"{APP_NAME}-{_validate_version(version)}-windows-x64-setup.exe"


def checksum_filename(installer_name: str) -> str:
    """Return the checksum sidecar name for an installer asset."""
    return f"{installer_name}.sha256"


def release_tag(version: str) -> str:
    """Return the Windows tag, e.g. v4.0.1.4-windows."""
    return f"v{_validate_version(version)}-windows"


def sha256_file(path: str | Path) -> str:
    """Hash a file in chunks so large installers do not fill memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checksum_line(path: str | Path) -> str:
    """Return a sha256sum-compatible line for the given file."""
    file = Path(path)
    return f"{sha256_file(file)}  {file.name}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="installer to hash")
    args = parser.parse_args()
    print(checksum_line(args.file))


if __name__ == "__main__":
    main()
