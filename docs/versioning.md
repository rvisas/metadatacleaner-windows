# Versioning

This project is an unofficial Windows port of Metadata Cleaner. Its version
number must answer two questions at a glance:

1. Which upstream release does it contain?
2. How many port revisions have been made on top of that release?

The answer is a four-component version:

```text
MAJOR.MINOR.PATCH.PORT
4    .0    .1    .6
```

`4.0.1` is the upstream base. The final `.6` is the Windows port revision. The
current release is **4.0.1.6**.

The source of truth is [`version.json`](../version.json):

```json
{
  "upstream": "4.0.1",
  "port": 6
}
```

`scripts/versioning.py` composes the four-part version and checks that the
Meson, Inno Setup and build-script inputs agree:

```bash
python scripts/versioning.py current       # 4.0.1.6
python scripts/versioning.py check         # fails if the files drift
python scripts/versioning.py next-upstream 4.1.0   # 4.1.0.1
```

Upstream currently uses three-component versions only (`v4.0.0`, `v4.0.1`, and
every earlier tag). The script rejects a four-component upstream base instead
of silently producing a fifth component that Windows/Inno Setup cannot store.

## If upstream adopts four components

Windows `VS_FIXEDFILEINFO` and Inno Setup store at most four numeric components.
If upstream ever publishes something like `4.1.0.2`, the port **cannot** append a
fifth component to make `4.1.0.2.1`. `scripts/versioning.py` rejects that base
on purpose so the change is not made silently.

In that scenario, keep the full upstream version in `version.json` and release
notes, but choose an explicit Windows mapping, for example:

```json
{
  "upstream": "4.1.0.2",
  "windows_base": "4.1.0",
  "port": 1
}
```

The mapping must be documented in the release and kept stable. The alternative
is an independent monotonic Windows build number. There is no perfect way to
encode two independent revision levels in four numeric fields; the important
thing is to decide the mapping once and never generate a five-part version.

Upstream's tags have been three-component throughout its published history
(`v2.x`, `v3.x`, `v4.0.0`, `v4.0.1`), so this is a contingency, not the current
state.

## Rules

| Change | Example | Next version |
|---|---|---|
| Port-only fix or packaging change | Folder import fix on upstream 4.0.1 | `4.0.1.6` |
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
Tag:      v4.0.1.6-windows
Installer: MetadataCleaner-4.0.1.6-windows-x64-setup.exe
Sidecar:   MetadataCleaner-4.0.1.6-windows-x64-setup.exe.sha256
```

The `-windows` suffix identifies the port and never changes. Only the version
number changes.

## Upstream base

| Date | Upstream tag | Upstream version | Port version | Notes |
|---|---|---|---|---|
| 2026-11-08 | `v4.0.1` | 4.0.1 | 4.0.1.6 | Streaming folder imports, English documentation and SignPath policy |
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.5 | Custom About title and localized links |
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.4 | Spanish libadwaita catalogs and About links |
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.3 | Installer cleanup for stale Linux directories |
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.2 | Product name and Windows-only payload |
| 2026-11-07 | `v4.0.1` | 4.0.1 | 4.0.1.1 | Initial public port revision |
| 2026-11-07 | — | — | 4.0.2 (withdrawn) | Retired internal build number; it never represented an upstream release |

Confirm the upstream release before changing the base:

```bash
git ls-remote --tags https://gitlab.com/metadatacleaner/metadatacleaner.git
curl -sL https://gitlab.com/api/v4/projects/metadatacleaner%2Fmetadatacleaner/releases?per_page=1
```

## Releasing a port revision

1. Make the fix on the current upstream base.
2. Bump the last component in `meson.build`, the installer,
   `scripts/build-windows.sh`, `installer/launcher/MetadataCleaner.rc` and
   `CITATION.cff`.
3. Run the full test suite locally.
4. Tag `v4.0.1.N-windows` and push the tag.
5. The Release workflow builds, tests, signs when configured, and publishes the
   installer with checksums.

The updater compares four-component tuples, so `4.0.1.1` is newer than
`4.0.1.0`, `4.0.1.2` is newer than `4.0.1.1`, and `4.0.1.6` is newer than
`4.0.1.5`.

## Why not SemVer build metadata?

`4.0.1+windows.1` is valid SemVer build metadata, but build metadata is ignored
for precedence and is awkward in file names and Windows version resources. The
four-component form is explicit, sortable and accepted by the Windows installer
toolchain.
