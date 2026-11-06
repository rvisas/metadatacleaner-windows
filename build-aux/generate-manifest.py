#!/usr/bin/env python3
# SPDX-FileCopyrightText: Metadata Cleaner contributors
# SPDX-License-Identifier: GPL-3.0-or-later

# Builds the local dev/CI flatpak manifest from the vendored flathub one:
# same dependency modules, but the app module builds from the working tree
# instead of a pinned release tag, with devel options and tests enabled.

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLATHUB_MANIFEST = (
    ROOT
    / "build-aux"
    / "flathub-manifest"
    / "io.gitlab.metadatacleaner.metadatacleaner.yaml"
)
OUTPUT_MANIFEST = (
    ROOT / "build-aux" / "io.gitlab.metadatacleaner.metadatacleaner.json"
)

APP_MODULE_NAME = "metadatacleaner"


def main():
    manifest = yaml.safe_load(FLATHUB_MANIFEST.read_text())

    for module in manifest["modules"]:
        if isinstance(module, dict) and module.get("name") == APP_MODULE_NAME:
            module.pop("x-checker-data", None)
            module["sources"] = [{"type": "dir", "path": "../"}]
            module["config-opts"] = module.get("config-opts", []) + [
                "-Ddevel=true"
            ]
            module["run-tests"] = True
            break
    else:
        sys.exit(
            f"could not find '{APP_MODULE_NAME}' module in {FLATHUB_MANIFEST}"
        )

    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=4) + "\n")


if __name__ == "__main__":
    main()
