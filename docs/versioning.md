# Versioning

This project is an unofficial Windows port of Metadata Cleaner. Its version
number must answer two questions at a glance:

1. Which upstream release does it contain?
2. How many port revisions have been made on top of that release?

The answer is a four-component version:

```text
MAJOR.MINOR.PATCH.PORT
4    .0    .1    .1
```

`4.0.1` is the upstream base. The final `.1` is the Windows port revision. The
current release is **4.0.1.1**.

## Rules

| Change | Example | Next version |
|---|---|---|
| Port-only fix or packaging change | Folder import fix on upstream 4.0.1 | `4.0.1.2` |
| New upstream release with port changes | Upstream releases 4.0.2 | `4.0.2.1` |
| Upstream release with no port change yet | Upstream releases 4.0.2 | Rebase first; release `4.0.2.1` when the port is ready |
| Documentation-only change | README or AGENTS.md | No release required |

- Never increase `MAJOR.MINOR.PATCH` for a port-only change. A `4.0.2` from this
  repository would falsely imply that upstream published 4.0.2.
- The port revision starts at `.1` for every new upstream base. It is not a
  global counter.
- A version with three components is still accepted by the updater and is read
  as having port revision `.0`; new releases must use four components.
- The four-part form is also the Windows file version. Inno Setup writes it to
  `VersionInfoVersion`; Windows displays it in the file properties dialog.

## Tags and assets

```text
Tag:      v4.0.1.1-windows
Installer: MetadataCleaner-4.0.1.1-windows-x64-setup.exe
Sidecar:   MetadataCleaner-4.0.1.1-windows-x64-setup.exe.sha256
```

The `-windows` suffix identifies the port and never changes. Only the version
number changes.

## Upstream base

| Date | Upstream tag | Upstream version | Port version | Notes |
|---|---|---|---|---|
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.1 | Current base; upstream `main` at `17e0b56` |
| 2026-11-07 | — | — | 4.0.2 (withdrawn) | Retired internal build number; it never represented an upstream release |

Confirm the upstream release before changing the base:

```bash
git ls-remote --tags https://gitlab.com/metadatacleaner/metadatacleaner.git
curl -sL https://gitlab.com/api/v4/projects/metadatacleaner%2Fmetadatacleaner/releases?per_page=1
```

## Releasing a port revision

1. Make the fix on the current upstream base.
2. Bump the last component in `meson.build`, the installer and
   `scripts/build-windows.sh`.
3. Run the full test suite locally.
4. Tag `v4.0.1.N-windows` and push the tag.
5. The Release workflow builds, tests, signs when configured, and publishes the
   installer with checksums.

The updater compares four-component tuples, so `4.0.1.1` is newer than
`4.0.1.0`, and `4.0.1.2` is newer than `4.0.1.1`.

## Why not SemVer build metadata?

`4.0.1+windows.1` is valid SemVer build metadata, but build metadata is ignored
for precedence and is awkward in file names and Windows version resources. The
four-component form is explicit, sortable and accepted by the Windows installer
toolchain.
