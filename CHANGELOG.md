# Changelog

All notable changes to this port are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use the
four-part upstream-plus-port scheme described in
[`docs/versioning.md`](docs/versioning.md).

## [Unreleased]

## [4.0.1.4] - 2026-11-07

Fourth Windows port revision, based on upstream 4.0.1.

### Fixed

- The About dialog and its native GTK/libadwaita labels stay in Spanish; the
  runtime now keeps the Spanish catalogs instead of pruning all runtime
  locales. The menu entry uses **Metadata Cleaner** untranslated.
- About links point to this port: website and issue tracker to GitHub, an
  explicit upstream-project link, and documentation to the repository. The
  Weblate and Matrix links that only applied upstream were removed.

### Changed

- Added `version.json` and `scripts/versioning.py` as the source/check for the
  upstream-derived version.

## [4.0.1.3] - 2026-11-07

Third Windows port revision, based on upstream 4.0.1.

### Fixed

- Upgrades remove `share\applications`, `share\metainfo` and `share\dbus-1`
  left by earlier builds, so the Linux integration cannot survive an update.

## [4.0.1.2] - 2026-11-07

Second Windows port revision, based on upstream 4.0.1.

### Fixed

- `Metadata Cleaner` remains untranslated in Spanish; the window title, About
  entry, dialogs and shortcuts now use the proper noun verbatim.
- The Windows payload no longer includes Linux desktop entries, AppStream
  metadata, D-Bus activation files or their build dependencies.

### Changed

- Added regression tests for the product name and for Windows-only packaging
  scope.

## [4.0.1.1] - 2026-11-07

First public Windows port revision, based on upstream 4.0.1.

### Added

- Native C launcher with the bundled GTK4/Python runtime; no system Python,
  GTK or MSYS2 installation is required.
- Inno Setup installer with English and Spanish setup languages, per-user
  installation, Start Menu and optional desktop shortcuts, and an uninstaller.
- Explicit AppUserModelID and window icon so taskbar pins launch
  `MetadataCleaner.exe` instead of `pythonw.exe`.
- Automatic update checker for GitHub Releases with SHA-256 verification,
  download progress feedback and an in-place installer launch.
- In-place upgrades that reuse the previous installation directory and keep
  settings.
- Runtime tests for folder imports and thorough/lightweight cleaning against
  the built payload.
- Static guardrails for localization, version consistency, release naming and
  installer behavior.

### Fixed

- Folder selection now enumerates GIO children with
  `standard::name,standard::type`; without attributes every child looked
  unsupported and folders appeared empty.
- Spanish UI text from GTK templates is translated by binding the gettext
  domain through `libintl` on Windows.
- The installer language is persisted and applied to the application; Windows
  locale and English are used as fallbacks.
- Portuguese, French and the other unused upstream catalogs are no longer
  shipped; only English and Spanish remain.
- Stale `share/locale` content is removed during upgrades.

### Changed

- Release versioning uses `UPSTREAM.PORT` (for example `4.0.1.1`) instead of
  implying an upstream feature release. The earlier `4.0.2` Windows build
  number is withdrawn; upstream's current release is 4.0.1.
- Documentation is organized under `docs/` with English, lowercase file names.
- Added `AGENTS.md` for AI-assisted maintenance and a public security policy.

### Security

- Updates are fetched over HTTPS and verified against the release SHA-256
  before execution.
- The installer remains unsigned until a code-signing provider is approved;
  SHA-256 sidecars are published for manual verification.

## [4.0.1] - 2026-11-01

Upstream base release. See the
[upstream release notes](https://gitlab.com/metadatacleaner/metadatacleaner/-/releases/v4.0.1).
