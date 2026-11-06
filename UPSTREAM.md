# Upstream tracking

- **Upstream:** https://gitlab.com/metadatacleaner/metadatacleaner
- **License:** GPL-3.0-or-later
- **Relationship:** unofficial Windows port, kept as close to upstream as possible.

## Branches and remotes

| Ref | Purpose |
|---|---|
| `main` | Mirror of upstream `main`. No Windows-specific commits. |
| `windows` | `main` + the Windows port patches. This is the branch that is built. |
| `origin` | `github.com/rvisas/metadatacleaner-windows` |
| `upstream` | `gitlab.com/metadatacleaner/metadatacleaner` |

## Windows patches

The applied source is the source of truth; `patches/` keeps the diffs against the
upstream tag for review and rebasing.

| Patch | File | Reason |
|---|---|---|
| Relocatable paths | `src/metadata-cleaner.in` | Derive `LOCALE_DIR` and `PKGDATA_DIR` from `__file__` instead of a POSIX prefix. |
| Home path | `src/modules/file.py` | `C:\Users\...` is not a valid regex; use `startswith`. |
| Portal xattr | `src/modules/file.py` | `xattr::document-portal.host-path` only exists inside Flatpak. |
| PDF URIs | `libmat2/pdf.py` (mat2) | `Path.as_uri()` produces `file:///C:/...`; fixes drive letters and `#`/spaces/accents. |
| PDF temp fd | `libmat2/pdf.py` (mat2) | Close the `mkstemp` descriptor; Windows cannot delete an open file. |
| Archive rewrite | `libmat2/archive.py` (mat2) | `os.replace` and writable permissions for DOCX/ODT/EPUB. |

The two mat2 patches are carried in `patches/0002-mat2-windows.patch`. They are
applied to the mat2 version pinned by the build (`0.15.0` at the time of writing),
not vendored into this repository.

## Updating from upstream

```bash
git fetch upstream --tags
git checkout main
git merge --ff-only upstream/main

git checkout windows
git rebase main          # or: git rebase vX.Y.Z
# resolve conflicts, rebuild, test
git push --force-with-lease origin windows
```

After a rebase, rebuild and re-run the format tests (JPEG, PDF, DOCX, MP4) before
tagging a release.

## Versioning

Tags follow the upstream version plus a Windows revision:

```text
v4.0.1-windows.1
v4.0.1-windows.2   # port-only fixes
v4.1.0-windows.1   # new upstream base
```

The upstream base version is also recorded in the release notes, not in the
repository description.
