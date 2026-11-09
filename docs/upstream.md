# Upstream tracking

- **Upstream:** https://gitlab.com/metadatacleaner/metadatacleaner
- **Current base:** `v4.0.1` (upstream `main` at `17e0b56`, which adds a post-release Flatpak manifest sync)
- **Current port version:** `4.0.1.7` (see [`versioning.md`](versioning.md))
- **License:** GPL-3.0-or-later
- **Relationship:** unofficial Windows port, maintained as a patch set.

## Repository model

This repository does not share Git history with upstream. It contains the upstream
source tree at a pinned release plus the Windows patches, so the delta stays easy
to read and re-apply.

The directory layout is deliberately stable across upstream updates. New
upstream files are added under the existing `src/`, `data/` and `po/` trees;
there is no need to recreate the repository or rename the port's directories
when a new upstream tag appears.

| Ref | Purpose |
|---|---|
| `main` | Port source: upstream tree + Windows patches. |
| `origin` | `github.com/rvisas/metadatacleaner-windows` |
| `upstream` | Not configured by default. Add it only when updating (see below); it is used to fetch a tag and diff, never merged. |

## Windows patches

The applied source is the source of truth; `patches/` keeps the diffs against the
upstream tag for review and re-application.

| Patch | File | Reason |
|---|---|---|
| Relocatable paths | `src/metadata-cleaner.in` | Derive `LOCALE_DIR` and `PKGDATA_DIR` from `__file__` instead of a POSIX prefix. |
| Home path | `src/modules/file.py` | `C:\Users\...` is not a valid regex; use `startswith`. |
| Portal xattr | `src/modules/file.py` | `xattr::document-portal.host-path` only exists inside Flatpak. |
| Taskbar identity | `src/metadata-cleaner.in` + installer | Explicit AppUserModelID and window icon so pinned shortcuts resolve to the app. |
| Folder import | `src/modules/filestore.py` | Request `standard::name,standard::type` from GIO; an empty attribute list makes every child look unsupported. |
| Update check | `src/modules/updater.py` + `src/app.py` | Windows-only GitHub Releases check, SHA-256 verification and in-place installer launch. |
| PDF URIs | `libmat2/pdf.py` (mat2) | `Path.as_uri()` produces `file:///C:/...`; fixes drive letters and `#`/spaces/accents. |
| PDF temp fd | `libmat2/pdf.py` (mat2) | Close the `mkstemp` descriptor; Windows cannot delete an open file. |
| Archive rewrite | `libmat2/archive.py` (mat2) | `os.replace` and writable permissions for DOCX/ODT/EPUB. |

The two mat2 patches are carried in `patches/0002-mat2-windows.patch`. They are
applied to the mat2 version pinned by the build (`0.15.0` at the time of writing),
not vendored into this repository. The AppUserModelID/icon change is in
`patches/0003-windows-taskbar.patch`; the installer applies the matching ID to
the Start Menu and desktop shortcuts.

## Updating from upstream

1. Confirm the new upstream release and its tag:

   ```bash
   git ls-remote --tags https://gitlab.com/metadatacleaner/metadatacleaner.git
   curl -sL "https://gitlab.com/api/v4/projects/metadatacleaner%2Fmetadatacleaner/releases?per_page=1"
   ```

2. Add the upstream remote if it is not configured, then fetch the new tag:

   ```bash
   git remote add upstream https://gitlab.com/metadatacleaner/metadatacleaner.git
   git fetch upstream --tags
   git worktree add ../upstream-vX.Y.Z vX.Y.Z
   ```

3. Compare the new tree with the current base and re-apply the patches:

   ```bash
   git diff --no-index ../upstream-vX.Y.Z/src/metadata-cleaner.in src/metadata-cleaner.in
   git diff --no-index ../upstream-vX.Y.Z/src/modules/file.py src/modules/file.py
   # adjust the patched files, then regenerate patches/
   ```

4. Rebuild, run the format tests (JPEG, PDF, DOCX, MP4) and the full test suite.
   Update [`build.md`](build.md) if a dependency changed.

5. Reset the port revision to `.1` and bump the upstream base in
   `version.json`; then sync `meson.build`, `installer/metadatacleaner.iss`,
   `scripts/build-windows.sh` and [`versioning.md`](versioning.md). Run
   `python scripts/versioning.py check`. Example: upstream 4.0.2 becomes port
   `4.0.2.1`.

6. Commit, tag, and remove the temporary worktree:

   ```bash
   git worktree remove ../upstream-vX.Y.Z
   git tag v4.0.2.1-windows
   git push origin v4.0.2.1-windows
   ```

The Release workflow builds from that tag. Do not merge upstream history into
`main`; keeping this repository as a source snapshot plus patches is what makes
the Windows delta reviewable.

## Versioning

Port versions are `UPSTREAM.PORT`, for example `4.0.1.7`; tags add `-windows`.
The full rules, comparison behavior and release examples are in
[`versioning.md`](versioning.md).
