# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 4.0.1.4 | Yes |
| 4.0.1 and older | No |

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting:

1. Open the repository's **Security** tab.
2. Select **Report a vulnerability**.
3. Include the affected version, Windows version, reproduction steps and any
   relevant logs or sample files.

Do not open a public issue for a security problem. Please allow time for a fix
and a coordinated release before publishing details.

## Scope

Reports are especially useful for:

- the update checker and installer launch path;
- SHA-256 verification and downloaded file handling;
- arbitrary code execution or unintended file modification;
- privilege boundaries of the per-user installer;
- dependency and bundled-runtime vulnerabilities.

## Integrity and signing

Release assets include:

- `MetadataCleaner-<version>-windows-x64-setup.exe`;
- `MetadataCleaner-<version>-windows-x64-setup.exe.sha256`;
- `SHA256SUMS.txt`.

Verify the SHA-256 checksum before running an installer. The application checks
the checksum automatically before launching a downloaded update.

The installer is currently **unsigned**. Windows SmartScreen may show an
"Unknown publisher" warning; that is expected until code signing is configured.
See [`docs/code-signing.md`](docs/code-signing.md). Do not trust a build solely
because it has a filename that resembles a release asset; verify the checksum
and obtain it from this repository's Releases page.
