# Releasing

Releases are built by GitHub Actions from a tag. The local workspace must not
contain installers or build output. Versioning is defined in
[`versioning.md`](versioning.md).

## Naming

| Thing | Value for 4.0.1.4 |
|---|---|
| Tag | `v4.0.1.4-windows` |
| Installer | `MetadataCleaner-4.0.1.4-windows-x64-setup.exe` |
| Checksum sidecar | `MetadataCleaner-4.0.1.4-windows-x64-setup.exe.sha256` |
| Combined checksum | `SHA256SUMS.txt` |

`windows-x64` follows the convention used by OBS Studio
(`OBS-Studio-33.0.1-Windows-x64-Installer.exe`), HandBrake
(`HandBrake-1.11.2-x86_64-Win_GUI.exe`), qBittorrent
(`qbittorrent_5.3.0_x64_setup.exe`) and darktable
(`darktable-5.6.2-win64.exe`): the asset says which OS and architecture it is
for before anyone downloads it.

## Automatic release

`.github/workflows/release.yml` runs when a tag matching `v*-windows` is
pushed, and can also be started manually with a version:

```bash
git tag -a v4.0.1.4-windows -m "Metadata Cleaner 4.0.1.4 for Windows"
git push origin v4.0.1.4-windows
```

Or:

```bash
gh workflow run Release -f version=4.0.1.4
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

## Manual release

If the workflow is unavailable, build the payload in an MSYS2 UCRT64 shell:

```bash
VERSION=4.0.1.4 BUILD_ROOT="$TMPDIR/metadata-cleaner-build" \
  bash ./scripts/build-windows.sh
iscc /DAppVersion=4.0.1.4 \
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
gh release create v4.0.1.4-windows `
  $asset.FullName "$($asset.FullName).sha256" `
  --title "v4.0.1.4-windows" `
  --prerelease --generate-notes
```

## Verifying a download

Windows PowerShell:

```powershell
Get-FileHash .\MetadataCleaner-4.0.1.4-windows-x64-setup.exe -Algorithm SHA256
Get-Content .\MetadataCleaner-4.0.1.4-windows-x64-setup.exe.sha256
```

The two hashes must match. On Linux or macOS, after downloading the asset and
the sidecar into the same directory:

```bash
sha256sum -c MetadataCleaner-4.0.1.4-windows-x64-setup.exe.sha256
```

`SHA256SUMS.txt` contains the same line in `sha256sum` format.

## Tests

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
