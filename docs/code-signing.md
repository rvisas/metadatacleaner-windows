# Code signing on Windows

This project publishes a Win32 `.exe` installer, not an MSIX package. That
limits the practical signing options: Windows trusts Authenticode signatures
from certificates chaining to the Microsoft Trusted Root Program, and
SmartScreen treats signed and unsigned files differently.

This document records the options, not a promise that the project is already
signed. The current installer is unsigned and releases are pre-releases.

## Why signing matters

- The installer and launcher show **Unknown publisher** without a trusted
  signature.
- SmartScreen may show **Windows protected your PC** on first download.
- A signature proves the binary came from the publisher and was not modified
  after signing, provided the file is timestamped and verified.

A signature does **not** guarantee that SmartScreen stays silent. Since 2024,
OV and EV certificates follow the same reputation-building process: the first
downloads of a new file can still warn until Microsoft has enough telemetry.
Only Microsoft Store distribution currently guarantees no SmartScreen prompt.

## Options for an open-source Windows project

| Option | Cost | Publisher shown | SmartScreen | Notes |
|---|---|---|---|---|
| **SignPath Foundation** | Free for qualifying OSS | SignPath Foundation | Builds reputation over time | Best fit for this project. Certificate is issued to the foundation, not to the maintainer. Signing runs in CI; private key stays in an HSM. |
| **Microsoft Store (MSIX)** | Free developer account; Microsoft re-signs | Your Store publisher name | No warning for Store installs | Requires an MSIX package and Store certification. The current Inno Setup `.exe` is not MSIX; submitting a Win32 installer through the Store still requires the publisher to sign it. |
| **Azure Artifact Signing** (formerly Trusted Signing) | From about US$9.99/month | Your verified organization or individual | Reputation builds over time | Public Trust availability is limited: organizations in the USA, Canada, EU and UK; individuals in the USA and Canada. Requires a paid Azure subscription. |
| **Certum Open Source Code Signing** | From about €49/year (cloud) | “Open Source Developer” + your name | Reputation builds over time | Individual developers only; project must be public and non-commercial. It was free years ago; it is now paid. |
| **OV certificate** (DigiCert, Sectigo, GlobalSign, SSL.com) | Roughly US$150–300/year | Your verified legal name | Reputation builds over time | Standard choice for commercial distribution. Private key must be on an HSM or token. |
| **EV certificate** | Typically US$400+/year | Your verified legal name | Reputation builds over time; **no instant bypass since 2024** | Still useful for enterprise procurement, not for skipping SmartScreen. |
| **OSSign** | Free for qualifying OSS | OSSign | Reputation builds over time | Newer OSS signing program; at the time of writing its application queue was suspended. Check current status. |
| **Sigstore / cosign** | Free | No Windows publisher identity | Not a Windows trust path | Good for Linux artifacts, container images and transparency logs; not a substitute for Authenticode. |
| **Self-signed certificate** | Free | Whatever name you choose | Still warns; not trusted by other machines | Development and enterprise-managed deployments only. |

### Can SignPath and the Microsoft Store be used together?

Yes. They solve different distribution paths and are not mutually exclusive:

- **SignPath Foundation** signs the standalone Inno Setup `.exe` published on
  GitHub Releases. The publisher shown is **SignPath Foundation**, because the
  foundation owns the certificate and vouches that the binary was built from
  this public repository. It is not issued in the maintainer's personal name.
- **Microsoft Store** distributes an MSIX package. Microsoft re-signs the
  package with its Store identity, and Store installations do not get a
  SmartScreen warning. The publisher shown is the Partner Center publisher
  identity, not the SignPath certificate.

Using both is normal for a project that offers a direct installer and a Store
package. The important rule is to keep the two channels separate:

| Channel | Artifact | Signing | Updates |
|---|---|---|---|
| GitHub Releases | Inno Setup `.exe` | SignPath Foundation (or another Authenticode cert) | In-app updater downloads the next `.exe` |
| Microsoft Store | MSIX | Microsoft re-signs after certification | Store updates |

Do not install the Inno build and the Store/MSIX build side by side on the same
machine unless they use different package identities and you have tested
uninstall/upgrade behavior. They have separate update mechanisms and separate
uninstall entries.

Maintaining both installers is more work: two packaging jobs, two smoke tests,
two release artifacts and two sets of upgrade tests. Keep one shared source
tree and version number, and build both artifacts from the same tag.

## Should I also register with OSSign?

Not while SignPath is viable. OSSign is another free-for-OSS program, but:

- its application queue was suspended at the time of writing;
- it uses a different signing identity, so SmartScreen reputation does not
  carry over from SignPath;
- maintaining two certificates and two publisher identities fragments trust and
  adds release complexity.

Use OSSign only as a fallback if SignPath rejects the project. Do not collect
free certificates from multiple providers “just in case”: pick one signing
identity per distribution channel and stay consistent.

## Why not my name as publisher?

A code-signing certificate identifies the entity that the CA (or foundation)
verified and that is legally responsible for the signature. SignPath Foundation
is the certificate holder for its OSS program; it verifies the repository and
the CI build, not the individual maintainer's identity. That is why the
signature says **SignPath Foundation** rather than your name.

If having your own name as publisher matters, use a certificate issued to you
or your legal entity:

- **Certum Open Source Code Signing** — “Open Source Developer” plus your name;
- **Azure Artifact Signing** — your verified individual or organization;
- an OV/EV certificate from DigiCert, Sectigo, GlobalSign or SSL.com.

## Recommendation for this repository

1. Apply to **SignPath Foundation** for the Inno Setup installer.
2. Create a **Microsoft Store individual developer account** and evaluate an
   MSIX package separately; do not replace the working `.exe` yet.
3. Skip OSSign while SignPath is active.
4. If SignPath rejects the project, choose **Certum Open Source** or **Azure
   Artifact Signing** and keep that identity for all future `.exe` releases.

## What SignPath signs

| Artifact | Why |
|---|---|
| `MetadataCleaner.exe` | Native launcher the user runs |
| `MetadataCleaner-<version>-windows-x64-setup.exe` | Installer downloaded from Releases |
| `unins000.exe` | Uninstaller; Inno Setup can sign it with `SignedUninstaller=yes` |

Bundled dependencies (GTK, Python, exiftool, ffmpeg) keep their own signatures
and licenses. SignPath signs the project's own artifacts.

## SignPath application checklist

- Public repository: <https://github.com/rvisas/metadatacleaner-windows>
- OSI-approved license: GPL-3.0-or-later
- Reproducible CI build with a documented process
- Releases produced by the project, not uploaded prebuilt binaries
- No malware, telemetry or license circumvention

The project description can say:

> `metadatacleaner-windows` is an unofficial, GPL-3.0-or-later Windows port of
> the Metadata Cleaner GTK application. It is built from the upstream source
> tree plus a small set of documented Windows patches, using MSYS2 UCRT64,
> GTK4/libadwaita and PyGObject. It publishes one Inno Setup installer and
> wants to sign its launcher, installer and uninstaller so users can verify the
> publisher. The repository is public and contains full build instructions;
> release artifacts are generated from tagged commits.

## CI integration after approval

1. Build the payload and compile the installer in GitHub Actions.
2. Submit the unsigned installer, launcher and uninstaller to SignPath.
3. Download the signed artifacts and attach them to the GitHub Release.
4. Store the SignPath API token as a repository secret; never commit it.
5. Uncomment `SignTool` and `SignedUninstaller` in
   `installer/metadatacleaner.iss` only after the signing command exists.

The exact action name and parameters come with the SignPath project
configuration.

## Linux and the rest of the free-software world

Linux distributions do not use Authenticode or SmartScreen. They sign at the
package/repository layer:

- **Debian/Ubuntu**: maintainers sign `.changes`/`.dsc` uploads; archive and
  repository metadata are signed with GPG. Users trust the distro keyring.
- **Fedora/openSUSE**: packages are signed by the distribution build system;
  repository metadata is signed.
- **Flatpak**: OSTree commits and repository metadata are GPG-signed; Flathub
  manages its own signing infrastructure.
- **Snap**: the Snap Store signs revisions; developers publish through the
  store.
- **AppImage**: developers commonly sign with GPG and publish a detached
  signature or checksum; there is no OS-level trust prompt equivalent to
  SmartScreen.
- **Sigstore** is increasingly used for release provenance and keyless signing
  in CI, especially for container images and language packages.

None of those mechanisms make a Windows `.exe` trusted. Windows requires an
Authenticode signature from a certificate chaining to the Microsoft Trusted
Root Program, or distribution through the Microsoft Store.

## Current status

- Releases are marked **pre-release** while unsigned.
- SHA-256 sidecars and `SHA256SUMS.txt` are published for manual verification.
- The application verifies the SHA-256 of downloaded updates before running
  them.
- Do not describe the installer as signed until a signature is visible in the
  file properties and `signtool verify /pa` succeeds.
