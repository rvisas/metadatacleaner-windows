# AGENTS.md

Instructions for AI agents and maintainers working in this repository. Read
[`docs/architecture.md`](docs/architecture.md) and
[`docs/versioning.md`](docs/versioning.md) before changing code.

## Project

An unofficial, faithful Windows 10/11 x64 port of Metadata Cleaner 4.0.1
(GTK4/libadwaita). The cleaning engine is mat2. The repository is a pinned
upstream source tree plus a small set of reviewable Windows patches; it does
not share Git history with upstream.

## Hard rules

- **No build artifacts in the repository.** Never commit `dist/`, installers,
  `.exe`, wheels, caches or `__pycache__`. Build output belongs under a
  temporary directory or `RUNNER_TEMP`.
- **English only for paths and identifiers.** File names, directory names,
  classes, functions, variables, comments and commit messages are English.
  UI strings are English in source and Spanish in `po/es.po`.
- **Only English and Spanish.** The installer offers exactly those two
  languages. Do not add another catalog or an installer language.
- **The product name is a proper noun.** `Metadata Cleaner` is never
  translated, in any language or any UI string. Translate the surrounding
  words only; `tests/test_product_name.py` enforces this.
- **Windows-only payload.** Do not add Linux desktop integration, Flatpak,
  Flathub, AppStream, D-Bus activation or other OS-specific files that the
  Windows build does not use. `tests/test_windows_scope.py` enforces this.
- **Thorough cleaning is the default.** The lightweight switch must remain
  functional, but it is an explicit opt-in.
- **Do not increase the upstream version for port-only changes.** Use the
  four-part port version. See `docs/versioning.md`.
- **Test before pushing.** Run the full local suite; CI is not a substitute for
  local verification.
- **No secrets.** Tokens, certificates and private keys go in GitHub Actions
  secrets or the signing provider's vault, never in the repository.
- **Keep upstream changes reviewable.** Prefer a guarded Windows branch in the
  existing upstream file over a large rewrite. Regenerate `patches/` when a
  patched file changes.

## Layout

```text
src/                 Python application and generated entry point
data/                GSettings, icons and UI templates
po/                  Spanish catalog; English is the source language
installer/           Inno Setup script, C launcher, branding
scripts/             Payload build and release metadata
patches/             Diffs against upstream and the pinned mat2
tests/               Static guardrails and runtime tests
docs/                Architecture, build, release, upstream, versioning, signing
.github/workflows/   Tests and release automation
```

## Commands

Run tests (from the repository root):

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Build a payload (MSYS2 UCRT64 shell; output stays outside the repository):

```bash
export PATH=/ucrt64/bin:$PATH
VERSION=4.0.1.2 BUILD_ROOT="$TMPDIR/metadata-cleaner-build" \
  bash ./scripts/build-windows.sh
```

Compile the installer after the payload exists:

```bash
iscc /DAppVersion=4.0.1.2 \
  /DPayloadDir="$TMPDIR/metadata-cleaner-build\\payload" \
  /DOutputDir="$TMPDIR/metadata-cleaner-build\\installer" \
  installer/metadatacleaner.iss
```

Create a release from CI (preferred):

```bash
git tag -a v4.0.1.2-windows -m "Metadata Cleaner 4.0.1.2 for Windows"
git push origin v4.0.1.2-windows
# or: gh workflow run Release -f version=4.0.1.2
```

## Changing UI text

1. Edit the English string in `data/ui/*.ui` or the `_()` literal in Python.
2. Add or update the `msgid` in `po/es.po` with a non-empty Spanish `msgstr`.
3. Run `tests/test_localization.py` and the full suite.
4. Do not add a language that the installer does not offer.

## Changing the updater or release names

- Tags: `v<UPSTREAM>.<PORT>-windows`, for example `v4.0.1.2-windows`.
- Assets: `MetadataCleaner-<version>-windows-x64-setup.exe`.
- Update the regexes in `src/modules/updater.py`, `scripts/release_metadata.py`
  and `.github/workflows/release.yml`, plus their tests.
- The updater must verify SHA-256 before launching an installer.

## Definition of done

- The full suite passes locally.
- `git diff --check` is clean.
- No generated files are tracked.
- Version numbers agree across `meson.build`, the Inno Setup script and
  `scripts/build-windows.sh`.
- Documentation that mentions a command, path or version is updated.
- A public release is built by GitHub Actions, not by committing an installer.
