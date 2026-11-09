# Changelog

All notable changes to this port are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions use the
four-part upstream-plus-port scheme described in
[`docs/versioning.md`](docs/versioning.md).

## [4.0.1.7] - 2026-11-08

Seventh Windows port revision, based on upstream 4.0.1. This revision only
removes unused code and documentation; it does not change cleaning behavior.

### Added

- CodeQL analysis, build provenance attestations and documentation/repository
  guardrails.

### Changed

- Removed the unused `CreditsRole` widget and template, the credits icon, the
  unreferenced `style.css` and the shortcuts-dialog resource.
- Removed the non-functional Keyboard Shortcuts menu item, which pointed to a
  missing `app.shortcuts` action.
- Merged `docs/releasing.md` into `docs/versioning.md`.
- Folded licensing details into the README and removed `LICENSE.md`, the stale
  gettext template and the unused Pyright configuration.
- Removed unused imports from the application and details view.

## [4.0.1.6] - 2026-11-08

Sixth Windows port revision, based on upstream 4.0.1.

### Changed

- Folder and file imports now stream discoveries into the file list instead of
  collecting the entire tree before showing the first row.
- Replaced the per-directory recursive thread pools with one iterative walker
  and a shared, bounded add pool.
- Duplicate detection uses an indexed path set instead of scanning the whole
  `Gio.ListStore` for every file.
- Progress events are coalesced so a large import does not flood the GTK main
  loop.
- Added an automated Markdown link/anchor checker and a documentation test.
- Documentation, README, release notes and issue templates are English-only;
  the application UI remains English/Spanish.

### Added

- A code signing policy and a privacy policy for the SignPath Foundation
  application and the project's public signing/privacy commitments.
- A `Code signing policy` section on the project home page with the required
  SignPath statement, roles and links.

### Fixed

- File rows are now appended before metadata parsing, so the UI remains
  responsive while mat2 inspects a batch.
- Removed stale website/font licensing text and a broken Open Font License link
  from the licensing section.

## [4.0.1.5] - 2026-11-07

Fifth Windows port revision, based on upstream 4.0.1.

### Fixed

- The About dialog uses an explicit Spanish title and app-localized link
  labels (Website, Report an Issue, Support, Documentation, Upstream project)
  instead of relying on incomplete libadwaita translations.
- No built-in English Website/Report an Issue rows are shown; all project
  links point to this port, with a separate upstream-project link.

## [4.0.1.4] - 2026-11-07

Fourth Windows port revision, based on upstream 4.0.1.

### Fixed

- The About dialog and native GTK/libadwaita labels stay in Spanish; the
  runtime keeps the Spanish catalogs instead of pruning all runtime locales.

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
