#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Ronny Visa
# SPDX-License-Identifier: GPL-3.0-or-later

"""Validate relative links and anchors in the project's Markdown files.

GitHub renders the README as the project landing page and resolves relative
links from the repository root.  A renamed document or heading can therefore
break several paths at once.  This checker walks every tracked documentation
file, resolves relative targets, and verifies Markdown heading anchors.
"""

from __future__ import annotations

import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCUMENTATION_FILES = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "CODE_SIGNING_POLICY.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "LICENSE.md",
    ROOT / "PRIVACY.md",
    ROOT / "SECURITY.md",
    ROOT / "installer" / "README.md",
    *sorted((ROOT / "docs").glob("*.md")),
]

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def anchor_for(heading: str) -> str:
    """Return the GitHub-style slug for a Markdown heading."""
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def anchors_in(path: Path) -> set[str]:
    return {
        anchor_for(match.group(2))
        for match in HEADING_RE.finditer(path.read_text(encoding="utf-8"))
    }


def check_documentation() -> list[str]:
    """Return a list of broken relative links and anchors."""
    errors: list[str] = []
    for source in DOCUMENTATION_FILES:
        if not source.exists():
            errors.append(f"missing documentation file: {source}")
            continue
        text = source.read_text(encoding="utf-8")
        source_name = source.relative_to(ROOT)
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip().strip("<>")
            if raw.startswith(EXTERNAL_PREFIXES):
                continue
            if raw.startswith("#"):
                target = source
                fragment = raw[1:]
            else:
                path_part, separator, fragment = raw.partition("#")
                target = (source.parent / urllib.parse.unquote(path_part)).resolve()
                if not separator:
                    fragment = ""
            if not target.exists():
                errors.append(f"{source_name}: missing target {raw}")
                continue
            if fragment and target.suffix.lower() == ".md":
                if fragment not in anchors_in(target):
                    errors.append(
                        f"{source_name}: missing anchor {raw} "
                        f"(have {sorted(anchors_in(target))})"
                    )
    return errors


def main() -> int:
    errors = check_documentation()
    if errors:
        print("\n".join(errors))
        return 1
    print(f"checked {len(DOCUMENTATION_FILES)} Markdown files: all links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
