# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Check GitHub Releases for a newer Windows build.

The application is distributed as a standalone Inno Setup installer.  This
module deliberately has no GTK dependency so its release selection and
checksum verification can be tested without a display or network access.
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

RELEASES_URL = (
    "https://api.github.com/repos/rvisas/metadatacleaner-windows/releases"
    "?per_page=20"
)
_RELEASE_TAG = re.compile(
    r"^v(?P<version>\d+\.\d+\.\d+(?:\.\d+)?)-windows$"
)
_INSTALLER = re.compile(
    r"^MetadataCleaner-(?P<version>\d+\.\d+\.\d+(?:\.\d+)?)-windows-x64-setup\.exe$"
)
VersionTuple = tuple[int, int, int, int]
_CHUNK_SIZE = 64 * 1024


class UpdateError(RuntimeError):
    """Raised when a release or its installer cannot be used."""


@dataclass(frozen=True)
class Update:
    """A newer release and the installer asset to download."""

    version: str
    tag: str
    installer_url: str
    sha256: str = ""
    sha256_url: str = ""
    notes: str = ""


def parse_version(value: str) -> VersionTuple | None:
    """Return a comparable four-part version tuple, or None if invalid.

    Port releases use the upstream version plus a Windows revision, for
    example ``4.0.1.6``. Three-part upstream values are accepted and the
    missing revision is treated as zero.
    """
    match = re.fullmatch(
        r"(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?", value.strip()
    )
    if match is None:
        return None
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4) or 0),
    )


def _release_version(release: dict[str, Any]) -> tuple[str, VersionTuple] | None:
    tag = release.get("tag_name")
    if not isinstance(tag, str):
        return None
    match = _RELEASE_TAG.fullmatch(tag)
    if match is None:
        return None
    version = match.group("version")
    parsed = parse_version(version)
    if parsed is None:
        return None
    return version, parsed


def pick_update(
    releases: Iterable[dict[str, Any]], current_version: str
) -> Update | None:
    """Pick the newest published release that is newer than current_version."""
    current = parse_version(current_version)
    if current is None:
        raise UpdateError(f"Invalid current version: {current_version!r}")

    best: tuple[VersionTuple, Update] | None = None
    for release in releases:
        if release.get("draft"):
            continue
        version_info = _release_version(release)
        if version_info is None:
            continue
        version, parsed = version_info
        if parsed <= current:
            continue

        installer = None
        sidecar = ""
        for asset in release.get("assets", []):
            name = asset.get("name", "")
            match = _INSTALLER.fullmatch(name)
            if match and match.group("version") == version:
                installer = asset
            elif name == f"MetadataCleaner-{version}-windows-x64-setup.exe.sha256":
                sidecar = asset.get("browser_download_url", "")
        if installer is None:
            continue
        installer_url = installer.get("browser_download_url")
        if not isinstance(installer_url, str) or not installer_url.startswith(
            "https://"
        ):
            continue

        digest = installer.get("digest", "")
        sha256 = ""
        if isinstance(digest, str) and digest.startswith("sha256:"):
            sha256 = digest.removeprefix("sha256:").strip().lower()
        if sidecar and not sidecar.startswith("https://"):
            sidecar = ""
        if not sha256 and not sidecar:
            continue
        candidate = Update(
            version=version,
            tag=release.get("tag_name", ""),
            installer_url=installer_url,
            sha256=sha256,
            sha256_url=sidecar,
            notes=release.get("body", "") or "",
        )
        if best is None or parsed > best[0]:
            best = (parsed, candidate)
    return best[1] if best else None


def fetch_releases(
    url: str = RELEASES_URL, timeout: float = 10.0
) -> list[dict[str, Any]]:
    """Download the release list from the GitHub API."""
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MetadataCleaner-Windows",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.load(response)
    if not isinstance(data, list):
        raise UpdateError("GitHub returned an unexpected response")
    return data


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_from_url(url: str, timeout: float = 10.0) -> str:
    request = urllib.request.Request(
        url, headers={"User-Agent": "MetadataCleaner-Windows"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        line = response.read(256).decode("utf-8", "replace").strip()
    match = re.search(r"\b[0-9a-fA-F]{64}\b", line)
    if match is None:
        raise UpdateError("The release checksum file is malformed")
    return match.group(0).lower()


def download_update(
    update: Update, target_dir: Path | None = None, timeout: float = 60.0
) -> Path:
    """Download and verify the installer; return its path.

    The downloaded file is stored outside the application directory (the
    system temporary directory by default) so it never becomes a repository
    artifact.
    """
    expected = update.sha256
    if not expected:
        if not update.sha256_url:
            raise UpdateError("The release has no checksum")
        expected = _sha256_from_url(update.sha256_url, timeout=timeout)

    destination_dir = target_dir or (Path(tempfile.gettempdir()) / "MetadataCleaner")
    destination_dir.mkdir(parents=True, exist_ok=True)
    name = Path(urllib.parse.urlparse(update.installer_url).path).name
    if not name.endswith(".exe"):
        name = f"MetadataCleaner-{update.version}-windows-x64-setup.exe"
    destination = destination_dir / name
    temporary = destination.with_suffix(destination.suffix + ".part")

    digest = hashlib.sha256()
    request = urllib.request.Request(
        update.installer_url,
        headers={"User-Agent": "MetadataCleaner-Windows"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            with temporary.open("wb") as stream:
                for chunk in iter(lambda: response.read(_CHUNK_SIZE), b""):
                    digest.update(chunk)
                    stream.write(chunk)
        actual = digest.hexdigest()
        if actual.lower() != expected.lower():
            raise UpdateError(
                f"Checksum mismatch: expected {expected}, got {actual}"
            )
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return destination
