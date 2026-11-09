# Download Metadata Cleaner for Windows

Metadata Cleaner for Windows is distributed as a signed-or-pending Windows
installer through GitHub Releases.

## Latest release

1. Open the [Releases page](https://github.com/rvisas/metadatacleaner-windows/releases).
2. Download `MetadataCleaner-<version>-windows-x64-setup.exe`.
3. Download the matching `.sha256` file or `SHA256SUMS.txt`.
4. Verify the installer before running it:

   ```powershell
   $version = "4.0.1.6"
   $asset = "MetadataCleaner-$version-windows-x64-setup.exe"
   Get-FileHash ".\$asset" -Algorithm SHA256
   Get-Content ".\$asset.sha256"
   ```

   The hashes must match. If they do not, do not run the file.

## Requirements

- Windows 10 version 2004 (build 19041) or newer, or Windows 11.
- x64. ARM64 is not supported yet.
- No separate Python, GTK or MSYS2 installation is required.

## Code signing

**Free code signing provided by [SignPath.io](https://about.signpath.io),
certificate by [SignPath Foundation](https://signpath.org).**

The project is applying to the SignPath Foundation open-source programme. Until
that application is approved, release installers are unsigned and Windows
SmartScreen may show an unknown-publisher warning. The full policy, including
the artifacts covered and the project roles, is in
[`CODE_SIGNING_POLICY.md`](CODE_SIGNING_POLICY.md).

## Privacy

The application processes files locally. See [`PRIVACY.md`](PRIVACY.md) for the
optional GitHub update check and the complete privacy statement.

## License

GPL-3.0-or-later. See [`LICENSE`](LICENSE).
