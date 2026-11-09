# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Compose and check the upstream-derived Windows port version.

The upstream project uses three-component versions (4.0.1). The Windows port
adds a fourth component for its own revision, so the result is 4.0.1.7.
A future upstream 4.1.0 becomes 4.1.0.1, not 4.0.2.

Windows and Inno Setup accept at most four numeric components. If upstream
ever adopts a fourth component, the port must switch to an explicit mapping
instead of appending a fifth; this module rejects such a base so the decision
cannot be made accidentally.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "version.json"
_UPSTREAM = re.compile(r"^\d+\.\d+\.\d+$")


def compose_version(upstream: str, port: int) -> str:
    """Return ``upstream.port`` after validating the four-part contract."""
    if _UPSTREAM.fullmatch(upstream) is None:
        raise ValueError(
            f"upstream must have exactly three numeric components: {upstream!r}"
        )
    if port < 1:
        raise ValueError(f"port revision must be positive: {port!r}")
    return f"{upstream}.{port}"


def next_for_upstream(upstream: str) -> str:
    """Return the first port version for a new upstream release."""
    return compose_version(upstream, 1)


def read_version(path: Path = VERSION_FILE) -> tuple[str, int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    upstream = data.get("upstream")
    port = data.get("port")
    if not isinstance(upstream, str) or not isinstance(port, int):
        raise ValueError(f"invalid version file: {path}")
    compose_version(upstream, port)
    return upstream, port


def current_version() -> str:
    upstream, port = read_version()
    return compose_version(upstream, port)


def check_project() -> str:
    """Check the source-of-truth version against the build inputs."""
    version = current_version()
    meson = (ROOT / "meson.build").read_text(encoding="utf-8")
    installer = (ROOT / "installer" / "metadatacleaner.iss").read_text(
        encoding="utf-8"
    )
    script = (ROOT / "scripts" / "build-windows.sh").read_text(
        encoding="utf-8"
    )
    launcher_rc = (
        ROOT / "installer" / "launcher" / "MetadataCleaner.rc"
    ).read_text(encoding="utf-8")
    if f"version: '{version}'" not in meson:
        raise ValueError(f"meson.build does not contain {version}")
    if f'#define AppVersion "{version}"' not in installer:
        raise ValueError(f"the installer does not contain {version}")
    if f'VERSION="${{VERSION:-{version}}}"' not in script:
        raise ValueError(f"build-windows.sh does not contain {version}")
    numeric = version.replace(".", ",")
    if f"#define MC_VERSION {numeric}" not in launcher_rc:
        raise ValueError(
            f"launcher resource does not contain MC_VERSION {numeric}"
        )
    if f'#define MC_VERSION_STRING "{version}"' not in launcher_rc:
        raise ValueError(
            f"launcher resource does not contain MC_VERSION_STRING {version}"
        )
    return version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("current", help="print the current port version")
    subparsers.add_parser("check", help="verify all build inputs agree")
    next_parser = subparsers.add_parser(
        "next-upstream", help="print the first port version for a new base"
    )
    next_parser.add_argument("upstream", help="new upstream version, e.g. 4.1.0")
    args = parser.parse_args(argv)

    if args.command == "current":
        print(current_version())
    elif args.command == "check":
        print(check_project())
    elif args.command == "next-upstream":
        print(next_for_upstream(args.upstream))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
