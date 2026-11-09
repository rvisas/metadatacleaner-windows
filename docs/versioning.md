# Versioning

This project is an unofficial Windows port of Metadata Cleaner. Its version
number must answer two questions at a glance:

1. Which upstream release does it contain?
2. How many port revisions have been made on top of that release?

The answer is a four-component version:

```text
MAJOR.MINOR.PATCH.PORT
4    .0    .1    .7
```

`4.0.1` is the upstream base. The final `.7` is the Windows port revision. The
current release is **4.0.1.7**.

The source of truth is [`version.json`](../version.json):

```json
{
  "upstream": "4.0.1",
  "port": 7
}
```

`scripts/versioning.py` composes the four-part version and checks that the
Meson, Inno Setup and build-script inputs agree:

```bash
python scripts/versioning.py current       # 4.0.1.7
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
| Port-only fix or packaging change | Folder import fix on upstream 4.0.1 | `4.0.1.7` |
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

| Thing | Value for 4.0.1.7 |
|---|---|
| Tag | `v4.0.1.7-windows` |
| Installer | `MetadataCleaner-4.0.1.7-windows-x64-setup.exe` |
| Checksum sidecar | `MetadataCleaner-4.0.1.7-windows-x64-setup.exe.sha256` |
| Combined checksum | `SHA256SUMS.txt` |

`windows-x64` follows the convention used by OBS Studio
(`OBS-Studio-33.0.1-Windows-x64-Installer.exe`), HandBrake
(`HandBrake-1.11.2-x86_64-Win_GUI.exe`), qBittorrent
(`qbittorrent_5.3.0_x64_setup.exe`) and darktable
(`darktable-5.6.2-win64.exe`): the asset says which OS and architecture it is
for before anyone downloads it.

The `-windows` suffix identifies the port and never changes. Only the version
number changes.

## Upstream base

| Date | Upstream tag | Upstream version | Port version | Notes |
|---|---|---|---|---|
| 2026-11-08 | `v4.0.1` | 4.0.1 | 4.0.1.7 | Removed dead UI resources, merged release docs and dropped stale licensing/config files |
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

Releases are built by GitHub Actions from a tag. The local workspace must not
contain installers or build output.

1. Make the fix on the current upstream base.
2. Bump the last component in `meson.build`, the installer,
   `scripts/build-windows.sh` and `installer/launcher/MetadataCleaner.rc`.
3. Run the full test suite locally.
4. Tag `v4.0.1.N-windows` and push the tag.
5. The Release workflow builds, tests, signs when configured, and publishes the
   installer with checksums.

The updater compares four-component tuples, so `4.0.1.1` is newer than
`4.0.1.0`, `4.0.1.2` is newer than `4.0.1.1`, and `4.0.1.7` is newer than
`4.0.1.5`.

### Automatic release

`.github/workflows/release.yml` runs when a tag matching `v*-windows` is
pushed, and can also be started manually with a version:

```bash
git tag -a v4.0.1.7-windows -m "Metadata Cleaner 4.0.1.7 for Windows"
git push origin v4.0.1.7-windows
```

Or:

```bash
gh workflow run Release -f version=4.0.1.7
```

The job:

1. installs MSYS2 UCRT64 and the GTK/Python toolchain;
2. runs the same unit and launcher tests as CI;
3. builds the payload outside the repository, in `RUNNER_TEMP`;
4. runs the runtime folder-import and lightweight tests against that payload;
5. installs Inno Setup and compiles the installer in `RUNNER_TEMP`;
6. writes the `.sha256` sidecar and `SHA256SUMS.txt`;
7. creates a **pre-release** with the installer and both checksum files.

The workflow stays a pre-release until code signing is approved. Once the
installer is signed, change `prerelease: true` to `false` and release as stable.

### Manual release

If the workflow is unavailable, build the payload in an MSYS2 UCRT64 shell:

```bash
VERSION=4.0.1.7 BUILD_ROOT="$TMPDIR/metadata-cleaner-build" \
  bash ./scripts/build-windows.sh
iscc /DAppVersion=4.0.1.7 \
  /DPayloadDir="$TMPDIR/metadata-cleaner-build\\payload" \
  /DOutputDir="$TMPDIR/metadata-cleaner-build\\installer" \
  installer/metadatacleaner.iss
```

Then create the checksums and the draft release:

```powershell
$build = Join-Path $env:TEMP "metadata-cleaner-build"
$asset = Get-ChildItem (Join-Path $build "installer\*.exe") | Select-Object -First 1
$hash = (Get-FileHash $asset.FullName -Algorithm SHA256).Hash.ToLower()
"$hash  $($asset.Name)" | Set-Content "$($asset.FullName).sha256" -Encoding ascii
gh release create v4.0.1.7-windows `
  $asset.FullName "$($asset.FullName).sha256" `
  --title "v4.0.1.7-windows" `
  --prerelease --generate-notes
```

### Verifying a download

Windows PowerShell:

```powershell
Get-FileHash .\MetadataCleaner-4.0.1.7-windows-x64-setup.exe -Algorithm SHA256
Get-Content .\MetadataCleaner-4.0.1.7-windows-x64-setup.exe.sha256
```

The two hashes must match. On Linux or macOS, after downloading the asset and
the sidecar into the same directory:

```bash
sha256sum -c MetadataCleaner-4.0.1.7-windows-x64-setup.exe.sha256
```

`SHA256SUMS.txt` contains the same line in `sha256sum` format.

### Tests

`.github/workflows/tests.yml` runs on `main` and pull requests. It executes:

- `tests/test_windows_port.py`: static guardrails for the relocatable entry
  point, the Windows home-path check, the document-portal guard, the mat2
  patches, installer languages, in-place upgrades and the installer asset name;
- `tests/test_release_metadata.py`: tag and asset naming plus SHA-256
  generation;
- `tests/test_filestore.py`, `tests/test_localization.py`,
  `tests/test_lightweight.py`, `tests/test_updater.py` and
  `tests/test_update_ui.py`: folder discovery, Spanish/English catalogs,
  lightweight wiring and the update selector;
- `tests/test_runtime_folder.py` and `tests/test_runtime_lightweight.py`:
  run against the payload built by the release workflow;
- `tests/test_launcher.py`: compiles a fake `pythonw.exe` and the real native
  launcher, then asserts the environment, working directory and forwarded
  arguments. It is skipped outside Windows or when `gcc` is not available.

## Why not SemVer build metadata?

`4.0.1+windows.1` is valid SemVer build metadata, but build metadata is ignored
for precedence and is awkward in file names and Windows version resources. The
four-component form is explicit, sortable and accepted by the Windows installer
toolchain.
