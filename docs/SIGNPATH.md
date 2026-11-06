# Code signing with SignPath Foundation

This project is public and GPL-3.0-or-later, so it can apply to
[SignPath Foundation](https://signpath.org/), which provides free code signing
for open-source projects.

## Why

- Windows shows "Unknown publisher" and SmartScreen warnings for unsigned
  installers. A trusted signature removes that friction.
- SignPath issues a certificate from a trusted CA and performs the signing in
  their service; the private key never lives on a contributor machine or in the
  repository.
- Signing from the first release lets SmartScreen reputation accumulate early.

A self-signed certificate is only useful to test the signing pipeline: other
machines do not trust it and SmartScreen still warns.

## Eligibility checklist

- Public repository: https://github.com/rvisas/metadatacleaner-windows
- OSI-approved license: GPL-3.0-or-later
- Builds from source, with a documented build process (`docs/BUILD.md`)
- Releases are produced by the project, not uploaded prebuilt binaries
- Active project with a release process

## Application

1. Create an account at https://signpath.org/ and open the Foundation
   application form.
2. Provide the repository URL, license, project description, build instructions
   and the list of artifacts to sign.
3. Describe how builds are produced (GitHub Actions or a documented local build)
   and who approves releases.
4. Wait for approval. Do not add signing secrets to the repository.

Draft description:

> `metadatacleaner-windows` is an unofficial, GPL-3.0-or-later Windows port of
> the Metadata Cleaner GTK application. It is built from the upstream source
> tree plus a small set of documented Windows patches, using MSYS2 UCRT64,
> GTK4/libadwaita and PyGObject. The project publishes a single Windows
> installer built with Inno Setup and wants to sign its installer, launcher and
> uninstaller so users can verify the publisher. The repository is public and
> contains the full build instructions; release artifacts are generated from
> tagged commits.

## What gets signed

| Artifact | Why |
|---|---|
| `MetadataCleaner.exe` | Launcher the user runs |
| `MetadataCleaner-Setup-x.y.z.exe` | Installer downloaded from Releases |
| Uninstaller (`unins000.exe`) | Inno Setup can sign it with `SignedUninstaller=yes` |

Dependencies bundled in the payload (GTK, Python, exiftool, ffmpeg) keep their
own signatures/licenses; SignPath signs the project's own artifacts.

## CI integration (after approval)

SignPath provides a GitHub Action. The outline:

1. Build the payload and compile the installer in a GitHub Actions workflow.
2. Submit a signing request with the unsigned installer as the artifact.
3. Download the signed artifact and attach it to the GitHub Release.
4. Store the SignPath API token as a repository secret; never in the repo.

The exact action name and parameters come with the SignPath project
configuration after approval.

## Until approval

- Do not claim the installer is signed.
- Publish releases as unsigned, or keep them unpublished until signing is
  available.
- Optionally test the signing pipeline with a self-signed certificate locally;
  do not distribute that build.
